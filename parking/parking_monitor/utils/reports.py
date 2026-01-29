"""
Génération de rapports PDF pour le système de parking
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from django.utils import timezone
from datetime import datetime
import io


def generate_pdf_report(queryset, start_date=None, end_date=None):
    """
    Génère un rapport PDF de l'historique du parking
    
    Args:
        queryset: QuerySet des enregistrements ParkingStatus
        start_date: Date de début (optionnel)
        end_date: Date de fin (optionnel)
    
    Returns:
        io.BytesIO: Buffer contenant le PDF
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    story = []
    
    # Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.HexColor('#1a1a1a'),
        spaceAfter=30,
        alignment=1  # Centré
    )
    
    # Titre
    title = Paragraph("Rapport d'Occupation du Parking", title_style)
    story.append(title)
    story.append(Spacer(1, 0.2*inch))
    
    # Informations du rapport
    period_text = "Période: "
    if start_date and end_date:
        period_text += f"Du {start_date} au {end_date}"
    elif start_date:
        period_text += f"À partir du {start_date}"
    elif end_date:
        period_text += f"Jusqu'au {end_date}"
    else:
        period_text += "Toutes les données"
    
    period_para = Paragraph(period_text, styles['Normal'])
    story.append(period_para)
    
    date_para = Paragraph(
        f"Généré le: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}",
        styles['Normal']
    )
    story.append(date_para)
    story.append(Spacer(1, 0.3*inch))
    
    # Statistiques globales
    if queryset.exists():
        total_records = queryset.count()
        avg_occupancy = sum(r.occupancy_rate for r in queryset) / total_records
        max_occupied = max(r.occupied for r in queryset)
        full_count = queryset.filter(status='full').count()
        
        stats_data = [
            ['Statistiques', ''],
            ['Nombre total d\'enregistrements', str(total_records)],
            ['Taux d\'occupation moyen', f"{avg_occupancy:.1f}%"],
            ['Pic d\'occupation', f"{max_occupied} véhicules"],
            ['Nombre de fois complet', str(full_count)],
        ]
        
        stats_table = Table(stats_data, colWidths=[4*inch, 2*inch])
        stats_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4a90e2')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
        ]))
        
        story.append(stats_table)
        story.append(Spacer(1, 0.3*inch))
    
    # Tableau des données
    if queryset.exists():
        # En-têtes
        data = [['Date/Heure', 'Occupé', 'Disponible', 'Total', 'Taux (%)', 'Statut']]
        
        # Limiter à 100 lignes pour éviter les PDF trop longs
        limited_queryset = queryset[:100]
        
        for record in limited_queryset:
            status_display = 'Complet' if record.status == 'full' else 'Disponible'
            data.append([
                record.timestamp.strftime('%d/%m/%Y %H:%M'),
                str(record.occupied),
                str(record.available),
                str(record.total_spaces),
                f"{record.occupancy_rate:.1f}",
                status_display
            ])
        
        table = Table(data, colWidths=[1.5*inch, 0.8*inch, 0.8*inch, 0.8*inch, 0.8*inch, 1*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c3e50')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
        ]))
        
        story.append(table)
        
        if queryset.count() > 100:
            story.append(Spacer(1, 0.2*inch))
            note = Paragraph(
                f"<i>Note: Seuls les 100 premiers enregistrements sont affichés sur {queryset.count()} au total.</i>",
                styles['Normal']
            )
            story.append(note)
    else:
        no_data = Paragraph("Aucune donnée disponible pour la période sélectionnée.", styles['Normal'])
        story.append(no_data)
    
    # Construire le PDF
    doc.build(story)
    buffer.seek(0)
    
    return buffer
