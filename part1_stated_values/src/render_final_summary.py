"""Regenerate the one-page Part 1 final research summary from the active dataset."""
import json,statistics
from pathlib import Path
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Table,TableStyle,KeepTogether
import reportlab
ROOT=Path(__file__).resolve().parents[2]
O=ROOT/'part1_stated_values/outputs/review_v2'
OUT=ROOT/'part1_stated_values/Part1_Summary.pdf'

def main():
 rows=json.loads((O/'part1_values_reviewed.json').read_text(encoding='utf8'))
 eligible=[r for r in rows if r['eligible_for_provisional_analysis']]
 known=[r for r in rows if type(r.get('changed_from_prior')) is bool and r['eligible_for_provisional_analysis']]
 years={y:sum(r['year']==y for r in eligible) for y in range(2016,2025)}
 src=Path(reportlab.__file__).parent/'fonts'
 pdfmetrics.registerFont(TTFont('Vera',str(src/'Vera.ttf')))
 pdfmetrics.registerFont(TTFont('Vera-Bold',str(src/'VeraBd.ttf')))
 normal=ParagraphStyle('body',fontName='Vera',fontSize=9.15,leading=13,spaceAfter=10,textColor=colors.HexColor('#263346'))
 title=ParagraphStyle('title',parent=normal,fontName='Vera-Bold',fontSize=15.7,leading=19,spaceAfter=7)
 heading=ParagraphStyle('heading',parent=normal,fontName='Vera-Bold',fontSize=10.25,leading=14,spaceAfter=4)
 small=ParagraphStyle('small',parent=normal,fontSize=8.2,leading=11,spaceAfter=5)
 doc=SimpleDocTemplate(str(OUT),pagesize=letter,leftMargin=43,rightMargin=43,topMargin=35,bottomMargin=39)
 story=[]
 def add(text,style=normal):story.append(Paragraph(text,style))
 add('Part 1 | Corporate stated values, 2016-2024',title)
 add('<b>Research question.</b> How do large companies describe their identity and values on archived corporate websites, and how much does this language change from one year to the next? This analysis examines 50 specified companies across five sectors and nine years.',normal)
 add('Approach',heading)
 add('The Wayback Machine CDX service identifies annual candidate snapshots of official About, mission, values or equivalent pages. Visible text is extracted after removing common page chrome. Gemini-based language-model coding assigns up to nine thematic labels using numbered source evidence blocks, and compares adjacent available years. Invalid or missing rows are never filled using current-day material.',normal)
 add('Observed coverage and findings',heading)
 add(f'<b>{len(rows)}</b> required company-year inventory records were retained. <b>{len(eligible)}</b> existing sources across <b>{len(set(r["ticker"] for r in eligible))}</b> companies satisfy coding eligibility and have final owner-confirmed selection decisions. The remaining <b>{len(rows)-len(eligible)}</b> rows are unavailable, invalid or excluded; these do not imply that the companies lack values. Coverage increases from <b>{years[2016]}/50</b> in 2016 to <b>{years[2024]}/50</b> in 2024, strongly limiting direct cross-year comparisons.',normal)
 add(f'Among <b>{len(known)}</b> available year-on-year comparisons, <b>{sum(r["changed_from_prior"] for r in known)}</b> show a recorded change in extracted text and <b>{sum(r["changed_from_prior"] is False for r in known)}</b> are unchanged. These reflect wording and page composition, including marketing or recruitment modules, not necessarily a shift in company priorities.',normal)
 add('Source review and material corrections',heading)
 add('An earlier focused quality check corrected selected evidence and page-boundary problems: Chevron text missed by extraction was restored, unsupported labels were removed, and Abbott 2020 was excluded as unsuitable. The project owner subsequently confirmed completion of human source review with <b>no further corrections required</b>. The 140 accepted sources are marked as final; missing and excluded entries remain unselected. Earlier classifications and the original summary statistics were preserved.',normal)
 add('Research implications and limitations',heading)
 add('The nine themes are innovation, integrity, people, inclusion, customer, environment, community, security/privacy/safety, and performance. Some captures overrepresent recruitment pages, founding histories, awards or navigation; 23 coding-validation failures and ten comparison-validation failures remain outside the accepted series. Even reviewed source content may contain genre differences or boilerplate. Capture year is not authorship year; values language does not demonstrate behavior or commitment fulfillment.',normal)
 add('Use this output as a transparent, source-linked measure of stated themes for Parts 3 and 4, not as a complete historical account. A scalable next step is targeted source-family repair, semantic heading classification and stronger genre-aware extraction, with new revisions versioned separately.',small)
 def footer(c,d):
  c.setStrokeColor(colors.HexColor('#d3dce5'));c.line(43,31,569,31)
  c.setFillColor(colors.HexColor('#516070'));c.setFont('Vera',7.6);c.drawString(43,20,'Organizational Authenticity | Part 1 | Final reviewed-source research summary');c.drawRightString(569,20,str(d.page))
 doc.build(story,onFirstPage=footer,onLaterPages=footer)
 print('Saved',OUT)
if __name__=='__main__':main()
