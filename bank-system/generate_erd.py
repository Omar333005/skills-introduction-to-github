import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

fig, ax = plt.subplots(1, 1, figsize=(20, 14))
ax.set_xlim(0, 20)
ax.set_ylim(0, 14)
ax.axis('off')
fig.patch.set_facecolor('#F0F4F8')

HEADER_COLOR = '#1A3C6E'
BOX_COLOR = '#FFFFFF'
BORDER_COLOR = '#2C5F9E'
TEXT_COLOR = '#1A1A2E'
PK_COLOR = '#FFD700'
FK_COLOR = '#FF6B6B'
LINE_COLOR = '#2C5F9E'

def draw_table(ax, x, y, width, height, title, columns):
    row_h = 0.38
    total_h = 0.52 + len(columns) * row_h

    shadow = FancyBboxPatch((x + 0.07, y - total_h - 0.07), width, total_h,
                             boxstyle="round,pad=0.05", linewidth=0,
                             facecolor='#CCCCCC', zorder=1)
    ax.add_patch(shadow)

    header = FancyBboxPatch((x, y - 0.5), width, 0.5,
                             boxstyle="round,pad=0.05", linewidth=1.5,
                             edgecolor=BORDER_COLOR, facecolor=HEADER_COLOR, zorder=2)
    ax.add_patch(header)

    ax.text(x + width/2, y - 0.25, title, ha='center', va='center',
            fontsize=11, fontweight='bold', color='white', zorder=3,
            fontfamily='DejaVu Sans')

    body = FancyBboxPatch((x, y - total_h), width, total_h - 0.5,
                           boxstyle="round,pad=0.02", linewidth=1.5,
                           edgecolor=BORDER_COLOR, facecolor=BOX_COLOR, zorder=2)
    ax.add_patch(body)

    for i, (col, dtype, key) in enumerate(columns):
        cy = y - 0.5 - (i + 0.5) * row_h - 0.04
        if i % 2 == 0:
            row_bg = FancyBboxPatch((x + 0.05, cy - row_h/2 + 0.04), width - 0.1, row_h - 0.04,
                                     boxstyle="round,pad=0.01", linewidth=0,
                                     facecolor='#EEF4FF', zorder=2)
            ax.add_patch(row_bg)

        if key == 'PK':
            badge = FancyBboxPatch((x + 0.08, cy - 0.1), 0.28, 0.2,
                                   boxstyle="round,pad=0.02", linewidth=0.5,
                                   facecolor='#FFD700', edgecolor='#B8860B', zorder=3)
            ax.add_patch(badge)
            ax.text(x + 0.22, cy, 'PK', ha='center', va='center',
                    fontsize=5.5, fontweight='bold', color='#3B2000', zorder=4)
        elif key == 'FK':
            badge = FancyBboxPatch((x + 0.08, cy - 0.1), 0.28, 0.2,
                                   boxstyle="round,pad=0.02", linewidth=0.5,
                                   facecolor='#FF6B6B', edgecolor='#CC0000', zorder=3)
            ax.add_patch(badge)
            ax.text(x + 0.22, cy, 'FK', ha='center', va='center',
                    fontsize=5.5, fontweight='bold', color='white', zorder=4)
        else:
            pass

        col_color = '#8B0000' if key == 'PK' else ('#00008B' if key == 'FK' else TEXT_COLOR)
        weight = 'bold' if key in ('PK', 'FK') else 'normal'
        ax.text(x + 0.35, cy, col, ha='left', va='center',
                fontsize=7.5, color=col_color, fontweight=weight, zorder=3)
        ax.text(x + width - 0.1, cy, dtype, ha='right', va='center',
                fontsize=6.5, color='#666666', zorder=3)

    return (x + width/2, y - total_h/2)

tables = {
    'Customer': {
        'pos': (0.3, 13.2),
        'cols': [
            ('CustomerID', 'INT', 'PK'),
            ('FirstName', 'VARCHAR(50)', ''),
            ('LastName', 'VARCHAR(50)', ''),
            ('NationalID', 'VARCHAR(20)', ''),
            ('Phone', 'VARCHAR(15)', ''),
            ('Email', 'VARCHAR(100)', ''),
            ('Address', 'VARCHAR(200)', ''),
            ('DateOfBirth', 'DATE', ''),
        ]
    },
    'Branch': {
        'pos': (7.5, 13.2),
        'cols': [
            ('BranchID', 'INT', 'PK'),
            ('BranchName', 'VARCHAR(100)', ''),
            ('Location', 'VARCHAR(200)', ''),
            ('Phone', 'VARCHAR(15)', ''),
        ]
    },
    'Employee': {
        'pos': (14.2, 13.2),
        'cols': [
            ('EmployeeID', 'INT', 'PK'),
            ('FirstName', 'VARCHAR(50)', ''),
            ('LastName', 'VARCHAR(50)', ''),
            ('Position', 'VARCHAR(50)', ''),
            ('Salary', 'DECIMAL(12,2)', ''),
            ('HireDate', 'DATE', ''),
            ('Phone', 'VARCHAR(15)', ''),
            ('Email', 'VARCHAR(100)', ''),
            ('BranchID', 'INT', 'FK'),
        ]
    },
    'Account': {
        'pos': (0.3, 6.5),
        'cols': [
            ('AccountID', 'INT', 'PK'),
            ('AccountType', 'VARCHAR(20)', ''),
            ('Balance', 'DECIMAL(15,2)', ''),
            ('OpenDate', 'DATE', ''),
            ('Status', 'VARCHAR(20)', ''),
            ('CustomerID', 'INT', 'FK'),
            ('BranchID', 'INT', 'FK'),
        ]
    },
    'Transaction': {
        'pos': (0.3, 1.8),
        'cols': [
            ('TransactionID', 'INT', 'PK'),
            ('TransactionType', 'VARCHAR(20)', ''),
            ('Amount', 'DECIMAL(15,2)', ''),
            ('TransactionDate', 'DATETIME', ''),
            ('Description', 'VARCHAR(200)', ''),
            ('BalanceAfter', 'DECIMAL(15,2)', ''),
            ('AccountID', 'INT', 'FK'),
        ]
    },
    'Loan': {
        'pos': (7.5, 6.5),
        'cols': [
            ('LoanID', 'INT', 'PK'),
            ('LoanType', 'VARCHAR(50)', ''),
            ('Amount', 'DECIMAL(15,2)', ''),
            ('InterestRate', 'DECIMAL(5,2)', ''),
            ('MonthlyPayment', 'DECIMAL(12,2)', ''),
            ('StartDate', 'DATE', ''),
            ('EndDate', 'DATE', ''),
            ('Status', 'VARCHAR(20)', ''),
            ('CustomerID', 'INT', 'FK'),
            ('BranchID', 'INT', 'FK'),
        ]
    },
}

w = 5.5
centers = {}
for name, info in tables.items():
    x, y = info['pos']
    cx, cy = draw_table(ax, x, y, w, 0, name, info['cols'])
    centers[name] = (x, y, w, info['cols'])

def get_edge(x, y, w, cols, side):
    total_h = 0.52 + len(cols) * 0.38
    cx = x + w/2
    cy = y - total_h/2
    if side == 'right':
        return (x + w, cy)
    elif side == 'left':
        return (x, cy)
    elif side == 'bottom':
        return (cx, y - total_h)
    elif side == 'top':
        return (cx, y)

def draw_rel(ax, t1, t2, side1, side2, label1='1', label2='N'):
    x1, y1, w1, cols1 = centers[t1]
    x2, y2, w2, cols2 = centers[t2]
    p1 = get_edge(x1, y1, w1, cols1, side1)
    p2 = get_edge(x2, y2, w2, cols2, side2)

    ax.annotate('', xy=p2, xytext=p1,
                arrowprops=dict(
                    arrowstyle='->', color=LINE_COLOR,
                    lw=2.0,
                    connectionstyle='arc3,rad=0.0'
                ), zorder=1)

    mx = (p1[0] + p2[0]) / 2
    my = (p1[1] + p2[1]) / 2
    ax.text(p1[0] + (0.2 if side1=='right' else -0.2 if side1=='left' else 0),
            p1[1] + (0.15 if side1 in ('top','bottom') else 0),
            label1, fontsize=10, fontweight='bold', color='#1A3C6E', zorder=4,
            ha='center', va='center',
            bbox=dict(boxstyle='round,pad=0.15', facecolor='white', edgecolor='none'))
    ax.text(p2[0] + (-0.2 if side2=='right' else 0.2 if side2=='left' else 0),
            p2[1] + (-0.15 if side2 in ('top','bottom') else 0),
            label2, fontsize=10, fontweight='bold', color='#C0392B', zorder=4,
            ha='center', va='center',
            bbox=dict(boxstyle='round,pad=0.15', facecolor='white', edgecolor='none'))

draw_rel(ax, 'Customer', 'Account',    'bottom', 'top')
draw_rel(ax, 'Customer', 'Loan',       'right',  'left')
draw_rel(ax, 'Branch',   'Account',    'bottom', 'right')
draw_rel(ax, 'Branch',   'Employee',   'right',  'left')
draw_rel(ax, 'Branch',   'Loan',       'bottom', 'top')
draw_rel(ax, 'Account',  'Transaction','bottom', 'top')

ax.text(10, 13.7, 'Bank Database System — ERD',
        ha='center', va='center', fontsize=18, fontweight='bold',
        color=HEADER_COLOR, fontfamily='DejaVu Sans')

ax.text(10, 13.35, 'Entity Relationship Diagram',
        ha='center', va='center', fontsize=11, color='#555555')

legend_items = [
    mpatches.Patch(color='#8B0000', label='PK = Primary Key'),
    mpatches.Patch(color='#00008B', label='FK = Foreign Key'),
    mpatches.Patch(color=LINE_COLOR, label='1:N Relationship'),
]
ax.legend(handles=legend_items, loc='lower right', fontsize=9,
          framealpha=0.9, edgecolor=BORDER_COLOR)

plt.tight_layout(pad=0.5)
plt.savefig('/home/user/skills-introduction-to-github/bank-system/ERD_Bank_System.png',
            dpi=180, bbox_inches='tight', facecolor=fig.get_facecolor())
print("ERD image saved successfully!")
