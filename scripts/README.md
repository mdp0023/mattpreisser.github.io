# BibTeX to HTML Workflow

This system automatically converts your `publications.bib` file into formatted HTML in the `about_me.html` page.

## How It Works

1. **Maintain `publications.bib`**: Keep all your publications in the `publications.bib` file in BibTeX format
2. **GitHub Actions Workflow**: On every push, the workflow automatically:
   - Parses your `publications.bib` file
   - Generates formatted HTML
   - Updates the Publications section in `about_me.html`
   - Commits and pushes the changes

## File Format

Each publication should be in standard BibTeX format:

```bibtex
@article{key2024,
  author = {Preisser, M. and Author, B.},
  year = {2024},
  title = {Your Paper Title},
  journal = {Journal Name},
  volume = {10},
  number = {2},
  pages = {100--120},
  doi = {10.xxxx/xxxxx}
}
```

For papers under review, add a `status` field:

```bibtex
@article{key2026,
  author = {Preisser, M. and Author, B.},
  year = {2026},
  title = {Paper Title},
  journal = {Target Journal},
  status = {Under Review}
}
```

## Running Manually

To generate publications HTML without pushing to Git:

```bash
python scripts/process_bib.py
```

This outputs the generated HTML to stdout.

## Supported Entry Types

- `@article` - Journal articles (primary use)
- Others can be added as needed

## Notes

- Author names with "Preisser" or "M. Preisser" are automatically bolded
- Publications are numbered in reverse order (newest first by default)
- The workflow runs only when `publications.bib` is modified
