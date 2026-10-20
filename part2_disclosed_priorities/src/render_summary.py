"""Render the documented Part 2 results; no network requests."""
import argparse,json,statistics
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
def main():
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,default=ROOT/'part2_disclosed_priorities/outputs/proxy_v2');out=p.parse_args().output
 read=lambda n:json.loads((out/(n+'.json')).read_text(encoding='utf-8'))
 rows=[r for r in read('disclosure_metrics') if 'themes' in r];events=read('pandemic_paired_comparison');summary=read('coverage_summary')
 themes=list(rows[0]['themes']);rates={t:statistics.mean(r['themes'][t]['per_1000_words'] for r in rows) for t in themes}
 paired={t:statistics.mean(r['theme_rate_changes'][t] for r in events) for t in themes}
 import matplotlib
 matplotlib.use('Agg')
 import matplotlib.pyplot as plt
 plt.rcParams.update({'font.size':9,'axes.spines.top':False,'axes.spines.right':False})
 figures=out/'figures';figures.mkdir(exist_ok=True)
 fig,ax=plt.subplots(1,2,figsize=(10,3.8))
 ordered=sorted(themes,key=rates.get);ax[0].barh(ordered,[rates[t] for t in ordered],color='#287c8e');ax[0].set(xlabel='Mean mentions per 1,000 words',title='Theme attention: 443 proxies')
 years=list(range(2016,2025))
 for t in ['commitment','uncertainty','obligation']:
  ax[1].plot(years,[statistics.mean(r['language'][t]['per_1000_words'] for r in rows if r['year']==y) for y in years],label=t)
 ax[1].set(xlabel='Filing year',ylabel='Mean mentions per 1,000 words',title='Language markers: changing sample');ax[1].legend(fontsize=8)
 fig.tight_layout();fig.savefig(figures/'part2_themes_language.png',dpi=180);plt.close(fig)
 import reportlab
 from reportlab.pdfbase import pdfmetrics
 from reportlab.pdfbase.ttfonts import TTFont
 from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
 from reportlab.platypus import SimpleDocTemplate,Paragraph,Image,PageBreak
 from reportlab.lib.pagesizes import letter
 fonts=Path(reportlab.__file__).parent/'fonts'
 for name,file in [('Vera','Vera.ttf'),('Vera-Bold','VeraBd.ttf')]:pdfmetrics.registerFont(TTFont(name,str(fonts/file)))
 pdfmetrics.registerFontFamily('Vera',normal='Vera',bold='Vera-Bold',italic='Vera',boldItalic='Vera-Bold')
 styles=getSampleStyleSheet();styles['Heading1'].fontName='Vera-Bold';styles['Heading1'].fontSize=17;styles.add(ParagraphStyle(name='Small',fontName='Vera',fontSize=9.5,leading=13,spaceAfter=9))
 story=[]
 def title(t):story.append(Paragraph(t,styles['Heading1']))
 def para(t):story.append(Paragraph(t,styles['Small']))
 title('Part 2 | Priorities expressed in proxy statements')
 para(f"<b>Coverage:</b> {len(rows)} of 450 company-years ({len(rows)/450:.1%}), representing all 50 firms in 2016-2024. The pipeline collected one consistent disclosure type: definitive proxy statements filed as DEF 14A. It supports {summary['adjacent_year_pairs']} adjacent-year comparisons. Missing documents remain missing, never zero.")
 para('<b>Approach.</b> A transparent dictionary measures nine themes shared with Part 1, alongside commitment, uncertainty, obligation and COVID-related language. Counts are divided by document word count. This method is inexpensive, reproducible and scalable, but measures mentions rather than endorsement or actual behavior. Proxies contain management claims, shareholder proposals, governance, compensation and repeated headings.')
 para(f"<b>What appears most often:</b> inclusion ({rates['inclusion']:.3f}), integrity ({rates['integrity']:.3f}) and environment ({rates['environment']:.3f}) lead the mean mention rates per 1,000 words. The prominence of inclusion and integrity partly reflects board diversity and required governance language; it should not be read as proof that these firms prioritize these values in practice.")
 story.append(Image(str(figures/'part2_themes_language.png'),width=510,height=193.8))
 para('<b>Sector differences.</b> Environmental language is the most frequent theme in the Energy sample, while inclusion leads the other four sectors. Sector means pool unequal observations and reflect both business context and proxy composition. The output retains company-year rates so readers can inspect individual firms rather than relying only on sector averages.')
 language={t:statistics.mean(r['language'][t]['per_1000_words'] for r in rows) for t in rows[0]['language']}
 para(f"<b>Language and tone proxies:</b> mean uncertainty-marker rate is {language['uncertainty']:.3f}, obligation {language['obligation']:.3f}, and commitment {language['commitment']:.3f} per 1,000 words. Words such as 'may' and 'shall' often reflect legal drafting. These rates are limited linguistic indicators, not validated positive/negative sentiment.")
 story.append(PageBreak());title('Change over time, event context and limits')
 para(f"<b>Pandemic-period comparison:</b> {len(events)} companies have every required filing in 2018, 2019, 2021 and 2022. For each firm, the analysis subtracts its 2018-2019 average from its 2021-2022 average, excluding transition year 2020. Each company receives equal weight. WHO characterized COVID-19 as a pandemic on 11 March 2020, providing the event context [1].")
 para(f"The largest average increases among the nine themes are inclusion (+{paired['inclusion']:.3f}), people (+{paired['people']:.3f}) and environment (+{paired['environment']:.3f}) mentions per 1,000 words. COVID-marker rates rise by {statistics.mean(r['covid_marker_change'] for r in events):.3f}. These results show co-occurring disclosure shifts; they cannot isolate a pandemic effect from changing reporting practices, social movements, regulation or company circumstances.")
 para('<b>Source repairs and gaps.</b> Historical CIK corrections recovered BlackRock and most ExxonMobil years; Tesla 2018 now uses its annual proxy rather than an earlier special-meeting proxy. Seven gaps remain: AAPL 2018; AVGO 2016-2018; MCD 2022; SBUX 2024; XOM 2021. AAPL has a December 2017 filing for a 2018 meeting, while XOM 2021 uses DEFC14A, outside the strict form filter. Other gaps remain unresolved under the selected CIK/form/year policy; they do not prove the absence of corporate disclosure.')
 para('<b>Validity concerns.</b> Full proxies range from about 9,400 to 239,000 word tokens. Tables, repeated sections, shareholder proposals and board terminology can distort lexical rates. Evidence excerpts include diversity of board views and proposals opposed by management. No semantic speaker attribution or validated sentiment model is applied. Filing year is not fiscal year, and archive captures in Part 1 often occur after the proxy filing date.')
 para('<b>What to do with this result.</b> Use the data to identify candidate changes for closer reading and to build a provisional communication-alignment index. Do not treat these rates as measures of realized social performance. With more time, separate management narratives from shareholder proposals, validate a stratified sample of matches and nonmatches, resolve entity/form gaps and apply a consistent annual-meeting selection rule.')
 para('<b>Reproducibility and review.</b> Code, versioned dictionary, filing URLs, hashes, source candidates, missingness and evidence excerpts are retained. The uploaded working archive contained the 443 saved proxy texts; their normalized hashes were verified and lexical rates from 35 documents were recalculated offline. The compact submission omits raw downloads; the full working archive retains them. The project owner confirmed completing the source review with no additional corrections; original coverage gaps are retained.')
 para('[1] WHO, 11 March 2020 media briefing. Source: who.int/news-room/speeches/item/who-director-general-s-opening-remarks-at-the-media-briefing-on-covid-19---11-march-2020. SEC filing provenance is recorded per observation in inventory.json.')
 def footer(c,d):c.setFont('Vera',8);c.drawString(42,25,'Organizational Authenticity | Part 2 | Provisional disclosed priorities');c.drawRightString(570,25,str(d.page))
 SimpleDocTemplate(str(out/'Part2_Summary.pdf'),pagesize=letter,leftMargin=42,rightMargin=42,topMargin=32,bottomMargin=40).build(story,onFirstPage=footer,onLaterPages=footer)
 print('Saved Part2_Summary.pdf and figures')
if __name__=='__main__':main()
