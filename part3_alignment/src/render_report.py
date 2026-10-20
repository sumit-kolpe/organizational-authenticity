"""Render the reviewed-source alignment analysis; no network calls."""
import argparse,json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
def main():
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,default=ROOT/'part3_alignment/outputs/alignment_v1');a=p.parse_args();out=a.output
 read=lambda name:json.loads((out/(name+'.json')).read_text(encoding='utf-8'))
 s=read('summary');rows=read('alignment');groups=read('group_summary');sensitivity=read('sensitivity_checks');controls=read('negative_controls')
 import matplotlib
 matplotlib.use('Agg')
 import matplotlib.pyplot as plt
 plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False,'figure.dpi':140})
 figs=out/'figures';figs.mkdir(exist_ok=True)
 valid=[r for r in rows if r['score'] is not None]
 fig,axes=plt.subplots(1,2,figsize=(10,3.5))
 axes[0].hist([r['score'] for r in valid],bins=[i/10 for i in range(11)],color='#287c8e',edgecolor='white')
 axes[0].set(xlabel='Textual alignment (0-1)',ylabel='Company-years',title=f'Distribution: n = {len(valid)}',xlim=(0,1))
 years=[r for r in groups if r['group_type']=='year']
 axes[1].bar([str(r['group']) for r in years],[r['n'] for r in years],color='#576b8e')
 axes[1].set(ylabel='Scored company-years',title='Changing coverage (50 possible per year)',ylim=(0,50))
 axes[1].tick_params(axis='x',rotation=45)
 for i,r in enumerate(years):axes[1].text(i,r['n']+1,str(r['n']),ha='center',fontsize=8)
 fig.tight_layout();fig.savefig(figs/'distribution_coverage.png');plt.close(fig)
 fig,axes=plt.subplots(1,2,figsize=(10,3.5))
 cs=[r for r in controls if r['control_scope']=='same_sector_year']
 axes[0].scatter([r['mean_other_score'] for r in cs],[r['own_score'] for r in cs],s=13,alpha=.55,color='#287c8e')
 axes[0].plot([0,1],[0,1],color='#777777',linestyle='--')
 axes[0].set(xlabel='Other proxies: same sector and year',ylabel='Own proxy alignment',title='Negative control',xlim=(0,1),ylim=(0,1))
 sectors=[r for r in groups if r['group_type']=='sector']
 labels=[str(r['group'])+' (n='+str(r['n'])+')' for r in sectors]
 axes[1].barh(labels,[r['mean'] or 0 for r in sectors],color='#576b8e')
 axes[1].set(xlabel='Mean textual alignment',title='Sector means: unbalanced sample',xlim=(0,1))
 fig.tight_layout();fig.savefig(figs/'validation_sectors.png');plt.close(fig)
 from reportlab.lib import colors
 import reportlab
 from reportlab.pdfbase import pdfmetrics
 from reportlab.pdfbase.ttfonts import TTFont
 from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
 from reportlab.lib.pagesizes import letter
 from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Image,PageBreak,Table,TableStyle
 from xml.sax.saxutils import escape
 fontdir=Path(reportlab.__file__).parent/'fonts'
 pdfmetrics.registerFont(TTFont('Vera',str(fontdir/'Vera.ttf')))
 pdfmetrics.registerFont(TTFont('Vera-Bold',str(fontdir/'VeraBd.ttf')))
 pdfmetrics.registerFontFamily('Vera',normal='Vera',bold='Vera-Bold',italic='Vera',boldItalic='Vera-Bold')
 styles=getSampleStyleSheet();styles['Heading1'].fontName='Vera-Bold';styles['Heading1'].fontSize=17
 styles.add(ParagraphStyle(name='BodySmall',fontName='Vera',fontSize=9.5,leading=13,spaceAfter=8))
 story=[]
 def para(text):story.append(Paragraph(text,styles['BodySmall']))
 def title(text):story.append(Paragraph(text,styles['Heading1']))
 title('Part 3 | Stated values and disclosure alignment')
 para('Provisional analysis of archived values pages and DEF 14A proxy statements, 2016-2024.')
 para(f"<b>Coverage:</b> {s['scored_company_years']} of 450 company-years ({s['scored_company_years']/450:.1%}), across {s['scored_companies']} of 50 companies. There are {s['adjacent_scored_pairs']} adjacent-year score comparisons. Missing and ineligible records receive no score. Historical values-page availability is the principal constraint.")
 para('<b>What the score means.</b> Nine shared themes connect the two sources. Each stated theme receives equal weight; proxy themes are weighted by their dictionary mention rates. Cosine similarity measures how closely those profiles line up, from 0 (no overlap) to 1 (proportional profiles). It does not measure how many promises were fulfilled, or whether a company behaved authentically.')
 para(f"<b>Observed results:</b> mean {s['primary']['mean']:.3f}, median {s['primary']['median']:.3f}, range {s['primary']['min']:.3f}-{s['primary']['max']:.3f}. Giving each represented company equal weight yields a mean of {s['company_equal_weight_mean']:.3f}. These are descriptive summaries of the available sample.")
 story.append(Image(str(figs/'distribution_coverage.png'),width=510,height=178.5))
 para('<b>Variation.</b> The output tables provide year, sector and company summaries, together with adjacent-year changes. The sample grows over time, so a change in the yearly mean may reflect which companies are observed. Sector comparisons also mix different firms and years; they are not rankings of corporate virtue.')
 para(f"The variance of observed company means is {s['variance_of_company_means']:.4f}; average squared deviation within companies is {s['mean_squared_within_company_deviation']:.4f}. Unequal years per company and single-observation firms prevent interpreting these as clean between/within variance components.")
 story.append(PageBreak());title('Validity checks and practical limits')
 gap=s['negative_controls']['same_sector_year']['mean']
 para(f"<b>Negative control:</b> each stated-values profile was also compared with other companies' proxies in the same sector and year. Its own proxy scored only {gap:.3f} higher on average. This small separation suggests substantial generic vocabulary and limited company-specific discrimination. It is a descriptive diagnostic, not a significance test or validation of authenticity.")
 story.append(Image(str(figs/'validation_sectors.png'),width=510,height=178.5))
 lookup={r['check']:r for r in sensitivity}
 para(f"<b>Sensitivity:</b> log-transformed rates give mean {lookup['cosine_log_rates']['mean']:.3f}; removing integrity and inclusion gives {lookup['cosine_excluding_integrity_inclusion']['mean']:.3f}. Excluding specifically scope-flagged values sources leaves {lookup['remove_scope_flagged']['n']} observations, mean {lookup['remove_scope_flagged']['mean']:.3f}. Only {lookup['snapshot_before_proxy']['n']} archive captures precede or coincide with proxy filing. These alternate definitions/subsamples answer different questions and do not eliminate bias.")
 para('<b>Main threats.</b> (1) Sparse, uneven historical coverage limits representativeness. (2) Values and recruitment pages differ from proxies, which mix management claims, shareholder proposals, compensation and required governance. (3) Model-coded theme presence and dictionary frequencies have different errors; synonyms, negation and repeated boilerplate matter. (4) Capture dates, filing dates and corporate entity changes may misalign observations. (5) Both sources describe communications, not independently observed conduct.')
 para('<b>Checks completed:</b> panel keys, theme vocabulary, rate/count consistency, missing-data treatment, mathematical edge cases, sensitivity and negative-control calculations. Source URLs and provenance are retained. The project owner confirmed completing source review without further corrections, including retention of the three diagnostic cases. These checks remain exploratory and cannot establish actual organizational behavior.')
 para('<b>Use:</b> treat this as an exploratory textual alignment index. Preserve the limitations in any presentation or subsequent analysis. Reproducible code, input hashes and detailed result tables accompany this summary.')
 def footer(c,d):
  c.setFont('Vera',8);c.setFillColor(colors.HexColor('#555555'));c.drawString(42,25,'Organizational Authenticity | Part 3 | Provisional textual alignment');c.drawRightString(570,25,str(d.page))
 SimpleDocTemplate(str(out/'Part3_Summary.pdf'),pagesize=letter,rightMargin=42,leftMargin=42,topMargin=32,bottomMargin=40).build(story,onFirstPage=footer,onLaterPages=footer)
 print('Saved charts and summary to',out)
if __name__=='__main__':main()
