"""Render Part 4 exploratory results offline using finalized review statuses."""
import argparse,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
def main():
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,default=ROOT/'part4_exploration/outputs/exploration_v1');o=p.parse_args().output
 read=lambda n:json.loads((o/(n+'.json')).read_text(encoding='utf-8'))
 s=read('summary');pairs=read('pairs');loo=read('leave_one_company_out')
 import matplotlib
 matplotlib.use('Agg')
 import matplotlib.pyplot as plt
 plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False})
 figdir=o/'figures';figdir.mkdir(exist_ok=True)
 fig,ax=plt.subplots(1,2,figsize=(10,3.6))
 for i,b in enumerate([False,True]):
  vals=[r['absolute_score_change'] for r in pairs if r['recorded_text_changed'] is b]
  ax[0].scatter([i+(j%7-3)*.025 for j in range(len(vals))],vals,s=18,alpha=.65,color='#287c8e')
  ax[0].plot([i-.22,i+.22],[sum(vals)/len(vals)]*2,color='#d77927',linewidth=3)
 ax[0].set(xticks=[0,1],xticklabels=['Unchanged (n=30)','Changed (n=49)'],ylabel='Absolute alignment change',title='Recorded text change: primary sample',ylim=(0,.45))
 ax[1].scatter(range(len(loo)),[r['difference'] for r in loo],s=24,color='#576b8e');ax[1].axhline(0,color='#777777',linestyle='--')
 ax[1].axhline(s['primary']['changed_minus_unchanged_absolute_mean'],color='#d77927')
 ax[1].set(xlabel='Omitted company (alphabetical index)',ylabel='Changed minus unchanged mean',title='Leave-one-company-out influence')
 fig.tight_layout();fig.savefig(figdir/'text_changes_and_influence.png',dpi=180);plt.close(fig)
 fig,ax=plt.subplots(figsize=(9,3.4))
 ax.scatter([r['stated_profile_component'] for r in pairs],[r['proxy_profile_component'] for r in pairs],c=['#287c8e' if r['theme_set_changed'] else '#d77927' for r in pairs],alpha=.7,s=23)
 ax.axhline(0,color='#aaaaaa',linewidth=.8);ax.axvline(0,color='#aaaaaa',linewidth=.8)
 ax.set(xlabel='Stated-profile component (signed)',ylabel='Proxy-profile component (signed)',title='Exact score attribution: orange = unchanged stated theme set')
 fig.tight_layout();fig.savefig(figdir/'score_decomposition.png',dpi=180);plt.close(fig)
 import reportlab
 from reportlab.pdfbase import pdfmetrics
 from reportlab.pdfbase.ttfonts import TTFont
 from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
 from reportlab.lib.pagesizes import letter
 from reportlab.platypus import SimpleDocTemplate,Paragraph,Image,PageBreak
 fonts=Path(reportlab.__file__).parent/'fonts'
 for name,file in [('Vera','Vera.ttf'),('Vera-Bold','VeraBd.ttf')]:pdfmetrics.registerFont(TTFont(name,str(fonts/file)))
 pdfmetrics.registerFontFamily('Vera',normal='Vera',bold='Vera-Bold',italic='Vera',boldItalic='Vera-Bold')
 styles=getSampleStyleSheet();styles['Heading1'].fontName='Vera-Bold';styles['Heading1'].fontSize=17
 styles.add(ParagraphStyle(name='BodySmall',fontName='Vera',fontSize=9.5,leading=13,spaceAfter=9))
 story=[]
 def title(t):story.append(Paragraph(t,styles['Heading1']))
 def para(t):story.append(Paragraph(t,styles['BodySmall']))
 title('Part 4 | Do text changes track alignment shifts?')
 para('<b>Question.</b> Is the magnitude of annual textual alignment change larger when the archived values text is recorded as changed than when it is recorded as unchanged? This exploratory analysis uses the Part 1 comparison labels and the Part 3 index; it does not measure changes in actual corporate behavior.')
 para(f"<b>Sample:</b> {s['known_text_comparison_pairs']} adjacent-year comparisons across {s['companies_with_known_pairs']} companies have known text-change decisions: 49 changed and 30 unchanged. Another {s['unknown_text_comparison_pairs']} adjacent scored pairs have unknown decisions and are excluded from the primary comparison. Firms can appear in both groups.")
 p=s['primary'];diff=p['changed_minus_unchanged_absolute_mean']
 para(f"<b>Result:</b> mean absolute score change is {p['changed']['absolute_change']['mean']:.4f} for changed text and {p['unchanged']['absolute_change']['mean']:.4f} for unchanged text, a difference of only {diff:.4f} on the 0-1 score scale. Absolute change measures movement size, regardless of direction.")
 story.append(Image(str(figdir/'text_changes_and_influence.png'),width=510,height=183.6))
 l=s['leave_one_company_out_difference'];c=s['company_balanced_within_company_difference']
 para(f"<b>Company influence:</b> omitting one company at a time produces differences from {l['min']:.4f} to {l['max']:.4f}. The sign can reverse, so the positive pooled contrast is not stable to company removal. Among the {c['n']} firms with both kinds of comparison, an equal-weight average of within-firm differences is {c['mean']:.4f}; this is a smaller, different sample.")
 para('<b>Interpretation.</b> These results provide limited descriptive support for greater alignment movement in years with recorded text changes. They do not establish that text changes cause disclosure changes, or that an organization became more or less authentic. The leave-one-out range is an influence diagnostic, not a confidence interval.')
 story.append(PageBreak());title('What moves the index, and what remains uncertain')
 para('<b>Attribution.</b> Each score change is split into a stated-profile component and a proxy-profile component by averaging the two possible orders of updating the profiles. The signed components add exactly to total change. This is arithmetic attribution, not causal evidence; opposing components can cancel.')
 story.append(Image(str(figdir/'score_decomposition.png'),width=510,height=192.7))
 stable=s['unchanged_theme_absolute_alignment_change']
 para(f"Among {stable['n']} pairs with identical coded stated-theme sets, mean absolute alignment change is {stable['mean']:.4f}. Their movement comes algebraically from changing proxy profiles. Stable stated themes therefore do not imply a stable alignment score.")
 para(f"<b>Sensitivity:</b> using coded theme-set changes across all 96 adjacent pairs gives a difference of {s['theme_set_sensitivity_all_adjacent_pairs']['changed_minus_unchanged_absolute_mean']:.4f}. This classification is partly mechanical because those same themes enter the index. Excluding specifically scope-flagged endpoints gives {s['scope_sensitivity']['changed_minus_unchanged_absolute_mean']:.4f}. Neither check establishes causality.")
 para(f"<b>Four coding/comparison disagreements:</b> AAPL 2017, HAL 2022, HAL 2023 and INTC 2019 are labeled unchanged text but have different coded theme sets. These could reflect comparison scope or coding variation. Excluding them gives a primary difference of {s['excluding_label_theme_disagreements']['changed_minus_unchanged_absolute_mean']:.4f}. The project owner confirmed review with no further changes; their inconsistencies are retained and assessed in sensitivity analysis.")
 para('<b>Limitations.</b> Text-change labels include minor edits and capture changes to extracted content, not necessarily values. Historical coverage is selective, timing within the year is imperfect, and repeated observations are dependent. Values/recruitment pages and full proxies are different genres; dictionary mentions include shareholder and governance language. Part 3 also showed weak company-specific discrimination. Results describe communications, not verified behavior.')
 para('<b>Reproducibility:</b> included code retains pair-level data and source URLs, checks input hashes against Part 3, and verifies that attribution adds to each score change. The analysis runs offline. The project owner confirmed completing source review with no additional corrections. Results remain descriptive, not causal.')
 def footer(canvas,doc):
  canvas.setFont('Vera',8);canvas.drawString(42,25,'Organizational Authenticity | Part 4 | Exploratory analysis');canvas.drawRightString(570,25,str(doc.page))
 SimpleDocTemplate(str(o/'Part4_Summary.pdf'),pagesize=letter,leftMargin=42,rightMargin=42,topMargin=32,bottomMargin=40).build(story,onFirstPage=footer,onLaterPages=footer)
 print('Saved charts and Part4_Summary.pdf')
if __name__=='__main__':main()
