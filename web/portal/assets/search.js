/**
 * Access Paralegal Suite - Client Side Documentation Index & Search Engine
 */

const FAQ_INDEX = [
    {
        title: "Do I need an internet connection to use this software?",
        slug: "offline-security",
        snippet: "No! Access Paralegal Suite operates 100% offline on your local machine. Confidential files never touch any cloud storage.",
        keywords: ["offline", "security", "internet", "cloud", "confidential", "local", "connection"]
    },
    {
        title: "I reordered my PDFs in the queue. How does the software know the right order?",
        slug: "queue-ordering",
        snippet: "The engine reads the exact visual order from the Treeview list. Drag and drop exhibits precisely how they should be combined.",
        keywords: ["order", "queue", "reorder", "treeview", "drag", "drop", "sort"]
    },
    {
        title: "How do I force a document to jump to the top of a massive queue?",
        slug: "mass-queue-jump",
        snippet: "Double-click the '#' index column on any document and type its exact numerical target. The list updates instantly.",
        keywords: ["jump", "top", "index", "numeric", "force", "move", "massive", "queue"]
    },
    {
        title: "Why did my Bates Stamping number not reset to 1 when I opened the app today?",
        slug: "bates-ledger",
        snippet: "This is a feature! The encrypted Bates Ledger tracks matter prefix numbers to prevent malpractice duplicate sequences.",
        keywords: ["bates", "ledger", "registry", "reset", "last", "number", "prevent", "duplicate"]
    },
    {
        title: "Can I override the Bates Ledger if I want to start at 1?",
        slug: "bates-override",
        snippet: "Yes. Simply click inside the Start Index box and manually type your starting number. This overrides the ledger database.",
        keywords: ["override", "start", "bates", "manual", "type", "index", "ledger"]
    },
    {
        title: "Where is my Audit Log?",
        slug: "audit-logs",
        snippet: "The Merge_Audit_Log.txt generates natively inside the output folder and opens instantly upon task completion.",
        keywords: ["audit", "log", "defensibility", "receipt", "missing", "txt", "output", "location"]
    }
];

document.addEventListener("DOMContentLoaded", () => {
    const searchInput = document.getElementById("faq-search-input");
    const resultsContainer = document.getElementById("faq-search-results");

    if (!searchInput || !resultsContainer) return;

    searchInput.addEventListener("input", (e) => {
        const query = e.target.value.toLowerCase().trim();
        resultsContainer.innerHTML = "";

        if (query.length === 0) {
            resultsContainer.style.display = "none";
            return;
        }

        // Score matches based on title and keywords
        const matches = FAQ_INDEX.map(item => {
            let score = 0;
            if (item.title.toLowerCase().includes(query)) score += 10;
            
            const keywordMatches = item.keywords.filter(kw => kw.includes(query));
            score += keywordMatches.length;

            return { ...item, score };
        })
        .filter(item => item.score > 0)
        .sort((a, b) => b.score - a.score);

        if (matches.length === 0) {
            resultsContainer.innerHTML = `<div class="no-results">No matching articles found for "${query}"</div>`;
        } else {
            matches.forEach(match => {
                const card = document.createElement("div");
                card.className = "search-result-item";
                // Correct routing based on where the user is running search from
                const baseUrl = window.location.pathname.includes("/faq/") ? "../" : "faq/";
                const finalUrl = baseUrl + match.slug + "/";
                
                card.innerHTML = `
                    <a href="${finalUrl}">
                        <h5>${match.title}</h5>
                        <p>${match.snippet}</p>
                    </a>
                `;
                resultsContainer.appendChild(card);
            });
        }
        resultsContainer.style.display = "block";
    });

    // Close results container when clicking away
    document.addEventListener("click", (e) => {
        if (!searchInput.contains(e.target) && !resultsContainer.contains(e.target)) {
            resultsContainer.style.display = "none";
        }
    });
});
