"""Copy assets used by LaTeX document."""
import click
import os
import re
import shutil
import subprocess
import sys
import tempfile
from typing import IO, List
import zipfile


PATH_REGEX = r"^INPUT\s+(?P<path>.*)$"


def prepare_output_dir(ctx, param, value):
    if not value:
        tmpdir = tempfile.mkdtemp()
        value = os.path.join(tmpdir, "textractor")
        ctx.call_on_close(lambda: shutil.rmtree(tmpdir))
    return value


@click.command()
@click.argument('zip-file', type=click.File("wb"))
@click.option('-m', '--main-doc',
              type=click.Path(dir_okay=False, file_okay=True, readable=True),
              default="main.tex",
              help="Main LaTeX document.")
@click.option('-o', '--output-dir',
              type=click.Path(dir_okay=True, file_okay=False, exists=False),
              callback=prepare_output_dir,
              help="Output directory for clean copy.")
@click.option('-b', '--bib-file',
              type=click.Path(dir_okay=False, file_okay=True, readable=True),
              help="Bib file. Default assumes same name as main-doc.")
@click.option('-i', '--include',
              type=click.Path(dir_okay=False, file_okay=True, readable=True),
              multiple=True,
              help="Additional files to include.")
@click.pass_context
def textract(ctx, zip_file: IO, main_doc: str, output_dir: str,
             bib_file: str, include: List[str]) -> None:
    """Extracting build-essential files from a LaTeX project and zip them."""
    # record dependency files
    res = subprocess.run(["pdflatex", "-recorder", "-draftmode",
                          "-halt-on-error", main_doc])
    if res.returncode != 0:
        click.echo("=== FAILURE: Recording dependencies failed! ===", err=True)
        sys.exit(res.returncode)

    # locate dependency file
    base, ext = os.path.splitext(main_doc)
    dep_path = base + os.path.extsep + "fls"
    try:
        dep_file = open(dep_path)
    except FileNotFoundError:
        click.echo("Something went wrong. Cannot find dependency file %s."
                   % (dep_path,), err=True)
        sys.exit(2)

    if os.path.exists(output_dir):  # remove output_dir if already present
        click.confirm("This will remove all content in %s. Proceed?"
                      % output_dir, abort=True)
        shutil.rmtree(output_dir)

    # identify local assets
    assets = []
    assets.append(main_doc)
    if not bib_file:
        bib_file = base + os.path.extsep + "bib"
    if not os.path.exists(bib_file):
        click.echo("No bib file found. Specify one with -b", err=True)
        sys.exit(1)
    assets.append(bib_file)

    with dep_file:
        for line in dep_file:
            match = re.search(PATH_REGEX, line)
            if not match:
                continue
            source = match.group("path")
            if not os.path.isabs(source):
                # only include local dependencies
                assets.append(source)

    # add manual includes to assets
    assets.extend(include)

    abs_assets = [os.path.abspath(a) for a in assets]
    click.echo(os.linesep.join(assets))

    # ignore function for copytree
    def ignore_non_assets(src, names):
        ignores = []
        for name in names:
            path = os.path.join(src, name)
            if (path not in abs_assets and
                    not (os.path.isdir(path) and
                         any(a.startswith(path) for a in abs_assets))):
                ignores.append(name)
        return ignores

    zip_builder = zipfile.ZipFile(zip_file, "w")

    # custom copy function that both copies the files to a clear directory
    # and adds them to a zip archive if asked to
    def copy_and_zip(src: str, dst: str):
        shutil.copy2(src, dst)
        if zip_builder:
            zip_builder.write(src, os.path.relpath(dst, start=output_dir))

    shutil.copytree(
        os.path.dirname(os.path.abspath(main_doc)),
        output_dir,
        ignore=ignore_non_assets,
        copy_function=copy_and_zip,
    )

    zip_builder.close()
    zip_file.close()

    # test LaTeX build on clean copy
    oldwd = os.getcwd()
    os.chdir(output_dir)
    res = subprocess.run(["pdflatex", "-halt-on-error", main_doc])
    os.chdir(oldwd)
    if res.returncode != 0:
        click.echo("=== FAILURE: Test build failed! ===", err=True)
        os.remove(zip_file.name)  # remove to avoid accidental usage
        sys.exit(res.returncode)
    else:
        click.echo("=== SUCCESS: Test build succeeded! ===")


if __name__ == '__main__':
    textract()
