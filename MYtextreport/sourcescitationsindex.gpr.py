#------------------------------------------------------------------------
#
# SourcesCitations ReportIndex
#
#------------------------------------------------------------------------
# Version 4.2
# $Id: SourcesCitationsReport.py 2014-06-19 Frink hansulrich.frink@gmail.com $

plg = newplugin()
plg.id    = 'SourcesCitationsIndex'
plg.name  = _("Sources and Citations Index")
plg.description =  _("Provides Index for a source and Citations with notes")
plg.version = '1.0'
plg.gramps_target_version = '4.2'
plg.status = STABLE
plg.fname = 'sourcescitationsindex.py'
plg.ptype = REPORT
plg.authors = ["Uli22"]
plg.authors_email = ["hansulrich.frink@gmail.com"]
plg.category = CATEGORY_TEXT
plg.reportclass = 'SourcesCitationsIndex'
plg.optionclass = 'SourcesCitationsIndexOptions'
plg.report_modes = [REPORT_MODE_GUI, REPORT_MODE_BKI, REPORT_MODE_CLI]
plg.require_active = False