import os
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from datetime import datetime
from config import WEEKDAYS

def generate_weekly_report(week_menus, prix_semaine, co2, gaspillage_initial, gaspillage_prevu, num_students=150):
    """Génère un rapport PDF hebdomadaire"""
    # Création du dossier reports s'il n'existe pas
    if not os.path.exists('reports'):
        os.makedirs('reports')
        
    # Nom du fichier avec la date
    filename = f"reports/rapport_semaine_{datetime.now().strftime('%Y%m%d')}.pdf"
    doc = SimpleDocTemplate(filename, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []
    
    # Titre
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30
    )
    story.append(Paragraph("Rapport Hebdomadaire de Restauration", title_style))
    
    # Informations générales
    story.append(Paragraph(f"Semaine du {week_menus[0]['Date'].strftime('%d/%m/%Y')} au {week_menus[-1]['Date'].strftime('%d/%m/%Y')}", styles["Heading2"]))
    story.append(Spacer(1, 12))
    
    # Menus de la semaine
    story.append(Paragraph("Menus de la semaine", styles["Heading2"]))
    menu_data = [["Jour", "Entrée", "Plat", "Légumes", "Laitage", "Dessert"]]
    for menu in week_menus:
        menu_data.append([
            WEEKDAYS[menu['Date'].weekday()],
            menu['Entrée'],
            menu['Plat'],
            menu.get('Légumes', ''),
            menu.get('Laitage', ''),
            menu.get('Dessert', '')
        ])
    
    menu_table = Table(menu_data, colWidths=[1*inch, 1.5*inch, 1.5*inch, 1.5*inch, 1.5*inch, 1.5*inch])
    menu_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    story.append(menu_table)
    story.append(Spacer(1, 20))
    
    # Statistiques
    story.append(Paragraph("Statistiques", styles["Heading2"]))
    stats_data = [
        ["Métrique", "Valeur"],
        ["Coût total de la semaine", f"{prix_semaine * 5 * num_students:.2f}€"],
        ["Coût par enfant", f"{prix_semaine:.2f}€"],
        ["Empreinte CO2", f"{co2:.1f} kg"],
        ["Gaspillage moyen initial", f"{sum(gaspillage_initial)/len(gaspillage_initial):.1f}%"],
        ["Gaspillage moyen prévu", f"{sum(gaspillage_prevu)/len(gaspillage_prevu):.1f}%"]
    ]
    
    stats_table = Table(stats_data, colWidths=[3*inch, 3*inch])
    stats_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    story.append(stats_table)
    
    # Génération du PDF
    doc.build(story)
    return filename