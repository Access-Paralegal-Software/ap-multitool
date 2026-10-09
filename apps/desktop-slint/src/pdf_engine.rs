use lopdf::{Document, Object, StringFormat};
use lopdf::content::{Content, Operation};
use std::path::Path;

pub fn get_page_count(path: &Path) -> Result<usize, lopdf::Error> {
    let doc = Document::load(path)?;
    Ok(doc.get_pages().len())
}

pub fn stamp_pdf(
    in_path: &Path,
    out_path: &Path,
    prefix: &str,
    start_num: i32,
    padding: usize,
    auto_shrink: bool,
) -> Result<(), Box<dyn std::error::Error>> {
    let mut doc = Document::load(in_path)?;
    // Extract ObjectIds from values(), preserving physical page order
    let pages: Vec<lopdf::ObjectId> = doc.get_pages().values().copied().collect();
    let mut current_bates = start_num;

    for page_id in pages {
        let bates_text = format!("{}{:0width$}", prefix, current_bates, width = padding);
        current_bates += 1;

        let mut prepend_stream_opt = None;
        if auto_shrink {
            // Affine matrix: scale 95%, translate Y +36pt (0.5 in upward shift)
            let prepend_ops = vec![
                Operation::new("q", vec![]),
                Operation::new("cm", vec![
                    0.95.into(), 0.0.into(),
                    0.0.into(), 0.95.into(),
                    0.0.into(), 36.0.into(),
                ]),
            ];
            let prepend_content = Content { operations: prepend_ops }.encode()?;
            prepend_stream_opt = Some(doc.add_object(Object::Stream(lopdf::Stream::new(
                lopdf::Dictionary::new(),
                prepend_content,
            ))));
        }

        // Bates stamp text stream
        let mut append_ops = Vec::new();
        if auto_shrink {
            append_ops.push(Operation::new("Q", vec![]));
        }
        append_ops.extend(vec![
            Operation::new("BT", vec![]),
            Operation::new("Tf", vec![Object::Name(b"Helvetica".to_vec()), 10.into()]),
            Operation::new("Td", vec![460.0.into(), 18.0.into()]),
            Operation::new("Tj", vec![Object::String(bates_text.into_bytes(), StringFormat::Literal)]),
            Operation::new("ET", vec![]),
        ]);
        let append_content = Content { operations: append_ops }.encode()?;
        let append_stream = doc.add_object(Object::Stream(lopdf::Stream::new(
            lopdf::Dictionary::new(),
            append_content,
        )));

        if let Ok(page_obj) = doc.get_object_mut(page_id) {
            if let Ok(dict) = page_obj.as_dict_mut() {
                match dict.get(b"Contents") {
                    Ok(Object::Array(ref arr)) => {
                        let mut new_arr = Vec::new();
                        if let Some(prep) = prepend_stream_opt {
                            new_arr.push(Object::Reference(prep));
                        }
                        new_arr.extend(arr.clone());
                        new_arr.push(Object::Reference(append_stream));
                        dict.set("Contents", Object::Array(new_arr));
                    }
                    Ok(Object::Reference(orig_ref)) => {
                        let mut new_arr = Vec::new();
                        if let Some(prep) = prepend_stream_opt {
                            new_arr.push(Object::Reference(prep));
                        }
                        new_arr.push(Object::Reference(*orig_ref));
                        new_arr.push(Object::Reference(append_stream));
                        dict.set("Contents", Object::Array(new_arr));
                    }
                    _ => {
                        dict.set("Contents", Object::Reference(append_stream));
                    }
                }
            }
        }
    }

    doc.save(out_path)?;
    Ok(())
}
