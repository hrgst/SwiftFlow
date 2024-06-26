import json
import os
from typing import Any
import mistletoe
from mistletoe import HTMLRenderer
import sass
import yaml


def convert_markdown_to_html(markdown_content):
    ''' Convert markdown to HTML. '''
    return mistletoe.markdown(markdown_content, renderer=CustomHTMLRenderer)


def convert_markdown_file_to_html(markdown_path, html_path=None):
    ''' Overwrite a file generated HTML from markdown file. '''

    # Same path with markdown file if not defined `html_path`
    if html_path is None:
        html_path = markdown_path.replace('.md', '.html')

    # Read a markdown file
    markdown_content = read_file(markdown_path)
    # Convert and save to file
    html_content = convert_markdown_to_html(markdown_content)
    write_file(html_path, html_content)


def convert_scss_file_to_css(
    scss_path: str,
    export_path: str = None,
    need_map: bool = True
):
    ''' Convert a SCSS file to CSS file. '''

    # Export path will be same path with scss file if not defined `export_path`
    export_path = export_path or scss_path.replace('.scss', '.css')
    map_path = export_path + '.map' if need_map else None

    # Convert
    css_content, map_content = sass.compile(
        filename=scss_path,
        output_style='compressed',
        source_map_embed=need_map,
        source_map_filename=map_path)

    # Overwrite css and map file
    write_file(export_path, css_content)
    write_file(map_path, map_content)


def delete_file(path: str):
    ''' Delete a file '''
    os.remove(path)


def path_of(*paths: str):
    ''' Join paths. '''
    return os.path.abspath(os.path.join(*paths))


def read_file(
    path: str,
    is_json: bool = False,
    is_yaml: bool = False,
):
    ''' Read a file. '''
    with open(path, mode='r', encoding='utf8') as f:
        if is_json:
            return json.load(f)
        elif is_yaml:
            return yaml.load(f, yaml.SafeLoader)
        else:
            return f.read()


def write_file(
    path: str,
    content: Any,
    is_json: bool = False,
    is_yaml: bool = False,
):
    ''' Write a file. '''
    with open(path, mode='w', encoding='utf8') as f:
        if is_json:
            json.dump(content, f, ensure_ascii=False)
        elif is_yaml:
            yaml.dump(content, f, yaml.SafeDumper, allow_unicode=True)
        else:
            f.write(content)


class CustomHTMLRenderer(HTMLRenderer):
    ''' Renderer to convert markdown to HTML with mistletoe. '''

    def render_heading(self, token):
        ''' Convert headers like `# header` '''
        if token.level == 1:
            return f'<h3>{self.render_inner(token)}</h3>'
        elif token.level == 2:
            return f'<h4>{self.render_inner(token)}</h4>'
        elif token.level == 3:
            return f'<h5>{self.render_inner(token)}</h5>'
        else:
            return f'<p><b>{self.render_inner(token)}<b></p>'

    def render_link(self, token):
        ''' Convert links like `[sample](http://example.com/)` '''

        link_url = self.escape_url(token.target)
        link_text = self.render_inner(token)

        # Convert internal link if link is NOT started with `http`
        if not link_url.startswith('http'):
            link_url = '{% origin %}'+f'?page={link_url}'

        return f'<a href="{link_url}">{link_text}</a>'
