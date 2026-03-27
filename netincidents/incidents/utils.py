"""
Générateur de rapports PDF avec ReportLab
"""
from django.http import HttpResponse
from django.utils import timezone
import io


def generer_rapport_pdf(incidents, titre, utilisateur):
    """
    Génère un rapport PDF professionnel pour les incidents fournis.
    Utilise ReportLab si disponible, sinon génère un PDF basique.
    """
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib import colors
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import cm
        from reportlab.platypus import (
            SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
            HRFlowable, KeepTogether
        )
        from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2*cm,
            bottomMargin=2*cm,
            title=titre,
        )

        styles = getSampleStyleSheet()

        # Styles personnalisés
        style_titre = ParagraphStyle(
            'TitrePrincipal',
            parent=styles['Title'],
            fontSize=20,
            textColor=colors.HexColor('#1a3a5c'),
            spaceAfter=6,
            fontName='Helvetica-Bold',
        )
        style_sous_titre = ParagraphStyle(
            'SousTitre',
            parent=styles['Normal'],
            fontSize=11,
            textColor=colors.HexColor('#666666'),
            spaceAfter=4,
        )
        style_section = ParagraphStyle(
            'Section',
            parent=styles['Heading2'],
            fontSize=13,
            textColor=colors.HexColor('#1a3a5c'),
            spaceBefore=14,
            spaceAfter=6,
            fontName='Helvetica-Bold',
            borderPad=4,
        )
        style_normal = ParagraphStyle(
            'NormalCustom',
            parent=styles['Normal'],
            fontSize=9,
            leading=13,
        )
        style_label = ParagraphStyle(
            'Label',
            parent=styles['Normal'],
            fontSize=9,
            fontName='Helvetica-Bold',
            textColor=colors.HexColor('#333333'),
        )

        # Couleurs pour statuts/priorités
        COULEURS_PRIORITE = {
            'critique': colors.HexColor('#dc3545'),
            'haute': colors.HexColor('#fd7e14'),
            'moyenne': colors.HexColor('#0dcaf0'),
            'basse': colors.HexColor('#198754'),
        }
        COULEURS_STATUT = {
            'ouvert': colors.HexColor('#dc3545'),
            'en_cours': colors.HexColor('#ffc107'),
            'resolu': colors.HexColor('#198754'),
            'ferme': colors.HexColor('#6c757d'),
        }

        elements = []
        now = timezone.now()

        # ── EN-TÊTE ──────────────────────────────────────────────
        elements.append(Paragraph("🌐 NetIncidents", style_titre))
        elements.append(Paragraph(titre, style_sous_titre))
        elements.append(Paragraph(
            f"Généré le {now.strftime('%d/%m/%Y à %H:%M')} par {utilisateur.get_full_name() or utilisateur.username}",
            style_sous_titre
        ))
        elements.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#1a3a5c')))
        elements.append(Spacer(1, 0.4*cm))

        # ── RÉSUMÉ STATISTIQUES ───────────────────────────────────
        elements.append(Paragraph("Résumé", style_section))

        total = len(incidents)
        ouverts = sum(1 for i in incidents if i.statut == 'ouvert')
        en_cours = sum(1 for i in incidents if i.statut == 'en_cours')
        resolus = sum(1 for i in incidents if i.statut == 'resolu')
        critiques = sum(1 for i in incidents if i.priorite == 'critique')

        stats_data = [
            ['Total incidents', 'Ouverts', 'En cours', 'Résolus', 'Critiques'],
            [str(total), str(ouverts), str(en_cours), str(resolus), str(critiques)],
        ]
        stats_table = Table(stats_data, colWidths=[3.4*cm]*5)
        stats_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a3a5c')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 1), (-1, 1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 1), (-1, 1), 16),
            ('TEXTCOLOR', (0, 1), (0, 1), colors.HexColor('#1a3a5c')),
            ('TEXTCOLOR', (4, 1), (4, 1), colors.HexColor('#dc3545')),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#dee2e6')),
            ('ROWBACKGROUNDS', (0, 1), (-1, 1), [colors.HexColor('#f8f9fa')]),
            ('PADDING', (0, 0), (-1, -1), 8),
        ]))
        elements.append(stats_table)
        elements.append(Spacer(1, 0.4*cm))

        # ── LISTE DES INCIDENTS ────────────────────────────────────
        elements.append(Paragraph(f"Détail des incidents ({total})", style_section))

        if not incidents:
            elements.append(Paragraph("Aucun incident correspondant aux critères.", style_normal))
        else:
            # En-tête tableau
            entete = ['#', 'Titre', 'Catégorie', 'Priorité', 'Statut', 'Créé le', 'Assigné à']
            table_data = [entete]

            for inc in incidents:
                table_data.append([
                    str(inc.id),
                    Paragraph(inc.titre[:60] + ('...' if len(inc.titre) > 60 else ''), style_normal),
                    inc.get_categorie_display(),
                    inc.get_priorite_display().upper(),
                    inc.get_statut_display(),
                    inc.date_creation.strftime('%d/%m/%Y'),
                    inc.assigne_a.username if inc.assigne_a else '—',
                ])

            col_widths = [1*cm, 5.5*cm, 3*cm, 2*cm, 2*cm, 2*cm, 2*cm]
            t = Table(table_data, colWidths=col_widths, repeatRows=1)

            # Style de base
            table_style = [
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a3a5c')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
                ('ALIGN', (0, 0), (0, -1), 'CENTER'),
                ('ALIGN', (3, 0), (5, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('GRID', (0, 0), (-1, -1), 0.3, colors.HexColor('#dee2e6')),
                ('PADDING', (0, 0), (-1, -1), 5),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
            ]

            # Coloriser priorités et statuts
            for row_idx, inc in enumerate(incidents, start=1):
                # Priorité
                coul_p = COULEURS_PRIORITE.get(inc.priorite, colors.gray)
                table_style.append(('TEXTCOLOR', (3, row_idx), (3, row_idx), coul_p))
                table_style.append(('FONTNAME', (3, row_idx), (3, row_idx), 'Helvetica-Bold'))
                # Statut
                coul_s = COULEURS_STATUT.get(inc.statut, colors.gray)
                table_style.append(('TEXTCOLOR', (4, row_idx), (4, row_idx), coul_s))
                table_style.append(('FONTNAME', (4, row_idx), (4, row_idx), 'Helvetica-Bold'))

            t.setStyle(TableStyle(table_style))
            elements.append(t)

        # ── FICHES DÉTAILLÉES (si rapport d'un seul incident) ──────
        if len(incidents) == 1:
            inc = incidents[0]
            elements.append(Spacer(1, 0.5*cm))
            elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#dee2e6')))
            elements.append(Paragraph("Fiche détaillée de l'incident", style_section))

            fiche_data = [
                ['Titre', inc.titre],
                ['Catégorie', inc.get_categorie_display()],
                ['Priorité', inc.get_priorite_display()],
                ['Statut', inc.get_statut_display()],
                ['Créé par', inc.cree_par.get_full_name() if inc.cree_par else '—'],
                ['Assigné à', inc.assigne_a.get_full_name() if inc.assigne_a else '—'],
                ['Date création', inc.date_creation.strftime('%d/%m/%Y %H:%M')],
                ['Date résolution', inc.date_resolution.strftime('%d/%m/%Y %H:%M') if inc.date_resolution else '—'],
                ['Durée résolution', f"{inc.duree_resolution()} heures" if inc.duree_resolution() else '—'],
            ]

            if inc.impact:
                fiche_data.append(['Impact', Paragraph(inc.impact, style_normal)])
            if inc.cause_racine:
                fiche_data.append(['Cause racine', Paragraph(inc.cause_racine, style_normal)])
            if inc.solution_appliquee:
                fiche_data.append(['Solution', Paragraph(inc.solution_appliquee, style_normal)])

            fiche_table = Table(fiche_data, colWidths=[4*cm, 13.5*cm])
            fiche_table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('GRID', (0, 0), (-1, -1), 0.3, colors.HexColor('#dee2e6')),
                ('PADDING', (0, 0), (-1, -1), 6),
                ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
                ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e9ecef')),
            ]))
            elements.append(fiche_table)

            # Commentaires
            commentaires = list(inc.commentaires.select_related('auteur').all())
            if commentaires:
                elements.append(Paragraph(f"Journal d'activité ({len(commentaires)} entrées)", style_section))
                for c in commentaires:
                    bloc = [
                        Paragraph(
                            f"<b>{c.auteur.username if c.auteur else 'Système'}</b> "
                            f"— {c.get_type_commentaire_display()} "
                            f"— {c.date_creation.strftime('%d/%m/%Y %H:%M')}",
                            style_label
                        ),
                        Paragraph(c.contenu, style_normal),
                        Spacer(1, 0.2*cm),
                    ]
                    elements.append(KeepTogether(bloc))

        # ── PIED DE PAGE ──────────────────────────────────────────
        elements.append(Spacer(1, 0.5*cm))
        elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#dee2e6')))
        style_pied = ParagraphStyle(
            'Pied', parent=styles['Normal'],
            fontSize=8, textColor=colors.HexColor('#999999'), alignment=TA_CENTER
        )
        elements.append(Paragraph(
            f"NetIncidents — Rapport confidentiel — {now.strftime('%d/%m/%Y')}",
            style_pied
        ))

        doc.build(elements)
        buffer.seek(0)

        filename = f"rapport_incidents_{now.strftime('%Y%m%d_%H%M')}.pdf"
        response = HttpResponse(buffer, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response

    except ImportError:
        # Fallback si ReportLab non installé
        response = HttpResponse(content_type='text/plain; charset=utf-8')
        response['Content-Disposition'] = 'attachment; filename="rapport.txt"'
        response.write(f"RAPPORT - {titre}\n")
        response.write(f"Généré le {timezone.now().strftime('%d/%m/%Y %H:%M')}\n")
        response.write("=" * 60 + "\n\n")
        for inc in incidents:
            response.write(f"#{inc.id} | {inc.titre}\n")
            response.write(f"  Priorité: {inc.get_priorite_display()} | Statut: {inc.get_statut_display()}\n")
            response.write(f"  Créé le: {inc.date_creation.strftime('%d/%m/%Y')}\n\n")
        return response
