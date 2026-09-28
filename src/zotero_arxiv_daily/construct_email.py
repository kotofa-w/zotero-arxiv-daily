from .protocol import Paper
from .daily_classics import ClassicPaper
from html import escape
import math


framework = """
<!DOCTYPE HTML>
<html>
<head>
  <style>
    .star-wrapper {
      font-size: 1.3em; /* 调整星星大小 */
      line-height: 1; /* 确保垂直对齐 */
      display: inline-flex;
      align-items: center; /* 保持对齐 */
    }
    .half-star {
      display: inline-block;
      width: 0.5em; /* 半颗星的宽度 */
      overflow: hidden;
      white-space: nowrap;
      vertical-align: middle;
    }
    .full-star {
      vertical-align: middle;
    }
  </style>
</head>
<body>

<div>
    __CONTENT__
</div>

<br><br>
<div>
To unsubscribe, remove your email in your Github Action setting.
</div>

</body>
</html>
"""

def get_empty_html():
  block_template = """
  <table border="0" cellpadding="0" cellspacing="0" width="100%" style="font-family: Arial, sans-serif; border: 1px solid #ddd; border-radius: 8px; padding: 16px; background-color: #f9f9f9;">
  <tr>
    <td style="font-size: 20px; font-weight: bold; color: #333;">
        No Papers Today. Take a Rest!
    </td>
  </tr>
  </table>
  """
  return block_template

def get_block_html(title:str, authors:str, rate:str, tldr:str, pdf_url:str,
                   affiliations:str=None, abstract_zh:str=None, guide:str=None,
                   guide_basis:str=None):
    if abstract_zh and guide:
        reading_html = (
            f'<strong>摘要译文：</strong> {escape(abstract_zh)}<br><br>'
            f'<strong>导读（依据{escape(guide_basis or "摘要")}）：</strong> '
            f'{escape(guide).replace(chr(10), "<br>")}'
        )
    else:
        reading_html = f'<strong>摘要：</strong> {escape(tldr or "")}'
    block_template = """
    <table border="0" cellpadding="0" cellspacing="0" width="100%" style="font-family: Arial, sans-serif; border: 1px solid #ddd; border-radius: 8px; padding: 16px; background-color: #f9f9f9;">
    <tr>
        <td style="font-size: 20px; font-weight: bold; color: #333;">
            {title}
        </td>
    </tr>
    <tr>
        <td style="font-size: 14px; color: #666; padding: 8px 0;">
            {authors}
            <br>
            <i>{affiliations}</i>
        </td>
    </tr>
    <tr>
        <td style="font-size: 14px; color: #333; padding: 8px 0;">
            <strong>Relevance:</strong> {rate}
        </td>
    </tr>
    <tr>
        <td style="font-size: 14px; color: #333; padding: 8px 0;">
            {reading_html}
        </td>
    </tr>

    <tr>
        <td style="padding: 8px 0;">
            <a href="{pdf_url}" style="display: inline-block; text-decoration: none; font-size: 14px; font-weight: bold; color: #fff; background-color: #d9534f; padding: 8px 16px; border-radius: 4px;">PDF</a>
        </td>
    </tr>
</table>
"""
    return block_template.format(
        title=escape(title), authors=escape(authors), rate=escape(str(rate)),
        reading_html=reading_html, pdf_url=escape(pdf_url or "", quote=True),
        affiliations=escape(affiliations or ""),
    )

def get_stars(score:float):
    full_star = '<span class="full-star">⭐</span>'
    half_star = '<span class="half-star">⭐</span>'
    low = 6
    high = 8
    if score <= low:
        return ''
    elif score >= high:
        return full_star * 5
    else:
        interval = (high-low) / 10
        star_num = math.ceil((score-low) / interval)
        full_star_num = int(star_num/2)
        half_star_num = star_num - full_star_num * 2
        return '<div class="star-wrapper">'+full_star * full_star_num + half_star * half_star_num + '</div>'


def get_classic_html(classic: ClassicPaper, guide_html: str | None = None) -> str:
    title = escape(classic.title)
    authors = escape(classic.authors.replace("; ", ", "))
    venue = escape(classic.venue)
    area = escape(classic.area)
    url = escape(classic.url, quote=True)
    return (
        '<section style="font-family: Arial, sans-serif; border: 1px solid #ddd; '
        'border-radius: 8px; padding: 16px; margin-top: 20px">'
        '<h2>学科经典</h2>'
        f'<h3>{title}</h3><p>{authors} · {classic.year} · {venue}</p>'
        f'<p>{area}</p><a href="{url}">阅读原文</a>'
        f'{guide_html or ""}</section>'
    )


def render_email(papers:list[Paper], classic: ClassicPaper | None = None,
                 classic_guide_html: str | None = None) -> str:
    parts = []
    if len(papers) == 0 and classic is None:
        return framework.replace('__CONTENT__', get_empty_html())
    
    for p in papers:
        #rate = get_stars(p.score)
        rate = round(p.score, 1) if p.score is not None else 'Unknown'
        author_list = [a for a in p.authors]
        num_authors = len(author_list)
        if num_authors <= 5:
            authors = ', '.join(author_list)
        else:
            authors = ', '.join(author_list[:3] + ['...'] + author_list[-2:])
        if p.affiliations is not None:
            affiliations = p.affiliations[:5]
            affiliations = ', '.join(affiliations)
            if len(p.affiliations) > 5:
                affiliations += ', ...'
        else:
            affiliations = 'Unknown Affiliation'
        parts.append(get_block_html(
            p.title, authors, rate, p.tldr, p.pdf_url, affiliations,
            p.abstract_zh, p.guide, p.guide_basis,
        ))

    content = '<br>' + '</br><br>'.join(parts) + '</br>' if parts else ''
    if classic is not None:
        if parts:
            content = '<h2>今日新论文</h2>' + content
        content += get_classic_html(classic, classic_guide_html)
    return framework.replace('__CONTENT__', content)
