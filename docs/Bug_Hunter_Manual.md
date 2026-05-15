# Access Paralegal Suite — Quality Assurance & Testing Manual

Welcome to the Access Paralegal Suite testing team! Your mission is to push this software to its limits and help us find bugs before our official launch.

## Step 1: Download & Activation

You are going to act exactly like a standard end-user. 
1. **Download:** Go to our temporary GitHub landing page at `[Insert GitHub Pages URL Here]` and download the `Access_Paralegal_Merge_Setup_v1.8.1.exe` file. *(We are using GitHub Pages right now while the Squarespace site is still under construction).*
2. **Launch:** Double-click the downloaded `.exe` file.
3. **Activate Your Pro Key:** When the app opens, look for the lock/activation prompt. Enter your secure testing key: `ACCESS_QA_MASTER_KEY` (or the specific key provided to you) to bypass the free-tier limits and unlock all Enterprise features.

---

## Step 2: Quick-Start Guide (The Happy Path)

Here is how the app is *supposed* to work under normal conditions. Try running this standard workflow first:
1. **Case Vault:** Enter a Case Number, Plaintiff, and Defendant in the secure vault fields at the top. Click "Lock & Secure".
2. **Load Documents:** Click the 📂 folder icon on the right side to select a folder full of PDFs on your computer.
3. **Reorder:** Drag and drop the documents in the visual list to put them in the correct exhibit order. 
4. **Merge:** Hit the big green "🚀 COMBINE & MERGE" button at the bottom.
5. **Verify:** A `Merge_Audit_Log.txt` file and your final merged PDF should automatically pop open on your screen when finished.

---

## Step 3: Important Feature Instructions (Try to Break These!)

### 1. Drag & Drop vs Explicit Ordering
- Try clicking and dragging multiple files around the queue.
- **Bug Hunt:** Double-click the `#` column on a specific document and explicitly type `1` to force it to the top. Did it move? Did the rest of the numbers shift correctly? If it ignores your input, log a bug.

### 2. The Offline Bates Registry Ledger
This app uses a highly advanced "Ledger" that remembers your last used Bates numbers offline.
- **Bug Hunt:** Type a prefix like `DEF-EX-` and run a Bates stamping job. Close the application entirely. Open it again, type `DEF-EX-` into the prefix box, click away, and see if the Start Index automatically jumps to the correct *next* number. If it forgets the number, log a bug!

### 3. High-Volume Threading
The application uses background threading to process documents without freezing your computer.
- **Bug Hunt:** Throw a folder with hundreds of pages at it. While it says "Processing...", try to drag the application window around your screen. If the window turns white/gray and Windows says "Not Responding", the threading optimization has failed.

---

## Step 4: Cross-Referencing the End-User FAQ

We will be hosting an official end-user FAQ on our GitHub repository. As you test, please cross-reference your experience against the official documentation to ensure the software behaves exactly as advertised to the end-users.

Read the official FAQ here: `[Insert Link to Github Repo FAQ.md Here]`

***

*Happy Hunting! If you encounter an error, take a screenshot of the error message and write down exactly what you clicked right before it happened.*
