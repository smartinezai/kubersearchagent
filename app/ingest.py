import io
import re
import zipfile
import requests
import frontmatter
from minsearch import Index


def read_repo_data(repo_owner, repo_name):
    url = f'https://codeload.github.com/{repo_owner}/{repo_name}/zip/refs/heads/main'
    resp = requests.get(url)

    if resp.status_code != 200:
        raise Exception(f"Failed to download repository: {resp.status_code}")

    repository_data = []
    zf = zipfile.ZipFile(io.BytesIO(resp.content))

    for file_info in zf.infolist():
        filename = file_info.filename
        filename_lower = filename.lower()
        if not (filename_lower.endswith('.md') or filename_lower.endswith('.mdx')):
            continue
        try:
            with zf.open(file_info) as f_in:
                content = f_in.read().decode('utf-8', errors='ignore')
                post = frontmatter.loads(content)
                data = post.to_dict()
                _, filename_repo = file_info.filename.split('/', maxsplit=1)
                data['filename'] = filename_repo
                repository_data.append(data)
        except Exception as e:
            print(f"Error processing {filename}: {e}")
            continue

    zf.close()
    return repository_data


def sliding_window(seq, size, step):
    if size <= 0 or step <= 0:
        raise ValueError("size and step must be positive")
    n = len(seq)
    result = []
    for i in range(0, n, step):
        chunk = seq[i:i+size]
        result.append({'start': i, 'chunk': chunk})
        if i + size >= n:
            break
    return result


def split_markdown_by_level(text, level=2):
    header_pattern = r'^(#{' + str(level) + r'} )(.+)$'
    pattern = re.compile(header_pattern, re.MULTILINE)
    parts = pattern.split(text)
    sections = []
    for i in range(1, len(parts), 3):
        header = parts[i] + parts[i+1]
        header = header.strip()
        content = ""
        if i+2 < len(parts):
            content = parts[i+2].strip()
        section = f'{header}\n\n{content}' if content else header
        sections.append(section)
    return sections


def hybrid_chunking(doc, min_size=100, max_size=2000, window_size=2000, step=1000):
    doc_copy = doc.copy()
    content = doc_copy.pop('content')
    sections = split_markdown_by_level(content, level=2)

    if not sections:
        chunks = sliding_window(content, window_size, step)
        result = []
        for chunk in chunks:
            c = doc_copy.copy()
            c['chunk'] = chunk['chunk']
            c['method'] = 'sliding_window'
            result.append(c)
        return result

    result = []
    pending = []

    for section in sections:
        if len(section) < min_size:
            pending.append(section)
        elif len(section) > max_size:
            if pending:
                merged = '\n\n'.join(pending)
                c = doc_copy.copy()
                c['chunk'] = merged
                c['method'] = 'merged_short_sections'
                result.append(c)
                pending = []
            chunks = sliding_window(section, window_size, step)
            for chunk in chunks:
                c = doc_copy.copy()
                c['chunk'] = chunk['chunk']
                c['method'] = 'sliding_window'
                result.append(c)
        else:
            if pending:
                pending.append(section)
                merged = '\n\n'.join(pending)
                c = doc_copy.copy()
                c['chunk'] = merged
                c['method'] = 'section_merged'
                pending = []
            else:
                c = doc_copy.copy()
                c['chunk'] = section
                c['method'] = 'section'
            result.append(c)

    if pending:
        merged = '\n\n'.join(pending)
        c = doc_copy.copy()
        c['chunk'] = merged
        c['method'] = 'merged_short_sections'
        result.append(c)

    return result


def index_data(repo_owner, repo_name):
    print(f"Downloading data from {repo_owner}/{repo_name}...")
    docs = read_repo_data(repo_owner, repo_name)
    print(f"Downloaded {len(docs)} documents. Chunking...")

    chunks = []
    for doc in docs:
        chunks.extend(hybrid_chunking(doc))
    print(f"Created {len(chunks)} chunks. Building index...")

    index = Index(
        text_fields=["chunk", "title", "filename"],
        keyword_fields=[]
    )
    index.fit(chunks)
    print("Index ready!")
    return index