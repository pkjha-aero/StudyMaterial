// MathJax 3 for two different producers of math on this site.
//
//  - Regular pages go through pymdownx.arithmatex in generic mode, which emits
//    \( ... \) and \[ ... \] inside elements classed `arithmatex`.
//  - Notebook pages are rendered by nbconvert, which bypasses the markdown pipeline
//    entirely. Its markdown cells keep Jupyter's own $ ... $ and $$ ... $$ delimiters
//    (it strips the backslash from \( ... \), so those cannot be used there).
//
// Both delimiter sets are therefore enabled, and both containers are opted in.
window.MathJax = {
  tex: {
    inlineMath: [["\\(", "\\)"], ["$", "$"]],
    displayMath: [["\\[", "\\]"], ["$$", "$$"]],
    processEscapes: true,
    processEnvironments: true,
    tags: "ams"
  },
  options: {
    // Process nothing by default; opt in the two containers that hold real math.
    // Shell variables such as `$HOME` live in <code>, which MathJax skips anyway.
    ignoreHtmlClass: ".*|",
    processHtmlClass: "arithmatex|jp-MarkdownCell"
  }
};

document$.subscribe(() => {
  MathJax.startup.output.clearCache();
  MathJax.typesetClear();
  MathJax.texReset();
  MathJax.typesetPromise();
});
