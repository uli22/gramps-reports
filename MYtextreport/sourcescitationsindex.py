#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2006  Donald N. Allingham
# Copyright (C) 2008       Brian G. Matherly
# Copyright (C) 2010       Jakim Friant
# Copyright (C) 2012       Hans Ulrich Frink
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
# Version 4.2
# $Id: SourcesCitationsReport.py 2014-06-19 Frink hansulrich.frink@gmail.com $
"""
Reports/Text Report.

Developed for gramps 3.4.2.1 under win 7 64bit

This is my first contribution to gramps, as well as my first python module,
so the programming style may in some way be unusual. Thanks to Enno Borgsteede
and Tim Lyons as well as other members of gramps dev for help 

PLEASE FEEL FREE TO CORRECT AND TEST.

This report lists all the citations and their notes in the database. so it 
is possible to have all the copies made from e.g. parish books together grouped 
by source and ordered by citation.page.

I needed such a report after I changed recording notes and media with the
citations and no longer with the sources.

works well in pdf, text and odf Format. The latter contains TOC which are also
accepted by ms office 2012 

Changelog:

Version 2.5:
- sources are sorted by source.author+title+publ+abbrev
- no German non translatables
- added Filter cf. PlaceReport.py
- changed citasource from gramps_id to citation rsp. source

Version 3.3:
- constructing dic directly
- or function
- sorting direct 
- Stylesheet in Options

Version 3.4:
- added .lower to sortfunctions to sources and to citation

Version 3.5: 
- get translation work
- include Persons names and gramps_id cited in the notes.

Version 4.2:
- adapted for gramps 4.2.0

next steps:

- have an index on Persons  
- have footer        

"""

#------------------------------------------------------------------------
#
# standard python modules
#
#------------------------------------------------------------------------
import time, string
from collections import defaultdict

#------------------------------------------------------------------------
#
# GRAMPS modules
#
#------------------------------------------------------------------------
import locale
from gramps.gen.const import GRAMPS_LOCALE as glocale
_ = glocale.translation.gettext
from gramps.gen.const import URL_HOMEPAGE
from gramps.gen.errors import ReportError
from gramps.gen.lib import NameType, EventType, Name, Date, Person, Surname
from gramps.gen.lib.date import gregorian
from gramps.gen.plug.docgen import (FontStyle, ParagraphStyle, GraphicsStyle,
                                    TableStyle, TableCellStyle,
                                    FONT_SERIF, PARA_ALIGN_RIGHT,
                                    PARA_ALIGN_LEFT, PARA_ALIGN_CENTER,
                                    IndexMark, INDEX_TYPE_TOC)
from gramps.gen.plug.menu import (BooleanOption, StringOption, NumberOption, 
                                  EnumeratedListOption, FilterOption, MediaOption,
                                  PersonOption, PlaceListOption, EnumeratedListOption,)
from gramps.gen.plug.report import Report
from gramps.gen.plug.report import utils as ReportUtils
from gramps.gen.plug.report import MenuReportOptions
from gramps.gen.plug.report import stdoptions
from gramps.gen.datehandler import displayer as _dd
from gramps.gen.datehandler import get_date
#------------------------------------------------------------------------
#
# SourcesCitationsIndex
#
#------------------------------------------------------------------------
class SourcesCitationsIndex(Report):
    """
    This report produces a summary of the objects in the database.
    """
    def __init__(self, database, options, user):
        """
        Create the SourceReport object that produces the report.
        
        The arguments are:

        database        - the GRAMPS database instance
        options         - instance of the Options class for this report
        user            - a gen.user.User() instance

        This report needs the following parameters (class variables)
        that come in the options class.
        
        Sources          - List of places to report on.
        """

        Report.__init__(self, database, options, user)
        self.__db = database
       
        menu = options.menu
        self.title_string = menu.get_option_by_name('title').get_value()
        self.subtitle_string = menu.get_option_by_name('subtitle').get_value()
        self.footer_string = menu.get_option_by_name('footer').get_value()
        self.showperson = menu.get_option_by_name('showperson').get_value()

        
        filter_option = menu.get_option_by_name('filter')
        self.filter = filter_option.get_filter()

        if self.filter.get_name() != '':
            # Use the selected filter to provide a list of source handles
            sourcefilterlist = self.__db.iter_source_handles()
            self.source_handles = self.filter.apply(self.__db, sourcefilterlist)
        else:
            self.source_handles = self.__db.get_source_handles()

    def write_report(self):
        """
        Overridden function to generate the report.
        """
        self.doc.start_paragraph("SRC-ReportTitle")
        title = self.title_string
        mark = IndexMark(title, INDEX_TYPE_TOC, 1)  
        self.doc.write_text(title, mark)
        self.doc.end_paragraph()
        
        self.doc.start_paragraph("SRC-ReportTitle")
        title = self.subtitle_string
        mark = IndexMark(title, INDEX_TYPE_TOC, 1)  
        self.doc.write_text(title, mark)
        self.doc.end_paragraph()
        
        self.listname()
                
    def listname(self):

        # build name dictionary
        # 
        penamedic ={}
        penamedic = defaultdict(set)
        i=0

        # Vornamen
        for pe in self.__db.get_person_handles():
            penamedic[self.__db.get_person_from_handle(pe).primary_name.get_first_name()].add(self.__db.get_person_from_handle(pe).gramps_id)

        # Einzelne Personen Namen
        for pe in self.__db.get_person_handles():
            penamedic[self.__db.get_person_from_handle(pe).primary_name.get_name()].add(self.__db.get_person_from_handle(pe).gramps_id)

        # Familiennamen
        
        for pe in self.__db.get_person_handles():
            person = self.__db.get_person_from_handle(pe)
            for name in [person.get_primary_name()] + person.get_alternate_names():
                if not name.get_surname().strip() == "":
                    penamedic[name.get_surname().strip()].add(self.__db.get_person_from_handle(pe).gramps_id)

            for name in [person.get_primary_name()] + person.get_alternate_names():
                if not name.get_surname().strip() in penamedic \
                    and not name.get_surname().strip() == "":
                    penamedic[name.get_surname().strip()].add(self.__db.get_person_from_handle(pe).gramps_id)
    
        self.doc.start_table("IndexTable", "SRC-IndexTable")
        column_titles = [_("LNR"),_("Person"), _("ID"), _("Vorkommen")]
        self.doc.start_row()
        for title in column_titles:
            self.doc.start_cell("SRC-TableColumn")
            self.doc.start_paragraph("SRC-ColumnTitle")
            self.doc.write_text(title)
            self.doc.end_paragraph()
            self.doc.end_cell()
        self.doc.end_row()                 

        nkeys = penamedic.keys()
        # nkeys.sort()   
#        nkeys.sort(cmp=locale.strcoll)
        
        for name in sorted(nkeys):
            i+=1
            self.doc.start_row()

            self.doc.start_cell("SRC-Cell")
            self.doc.start_paragraph("SRC-SourceDetails")
            self.doc.write_text(_("%s") %
                           i)
            self.doc.end_paragraph()
            self.doc.end_cell()

            self.doc.start_cell("SRC-Cell")
            self.doc.start_paragraph("SRC-SourceDetails")
            self.doc.write_text(_("%s") %
                           name)
            self.doc.end_paragraph()
            self.doc.end_cell()
     
            self.doc.start_cell("SRC-Cell")
            self.doc.start_paragraph("SRC-SourceDetails")
            for id in penamedic[name]:
                self.doc.write_text(_("%s, ") % 
                              id)
            self.doc.end_paragraph()
            self.doc.end_cell()
 
            self.doc.start_cell("SRC-Cell")
            self.doc.start_paragraph("SRC-SourceDetails")
            self.doc.write_text(_("%s") %
                         len(penamedic[name]))
            self.doc.end_paragraph()
            self.doc.end_cell()
    
            self.doc.end_row()
        self.doc.end_table()
        

#------------------------------------------------------------------------
#
# SourcesCitationsIndexOptions
#
#------------------------------------------------------------------------
class SourcesCitationsIndexOptions(MenuReportOptions):
    """
    SourcesCitationsAndPersonsOptions provides the options 
    for the SourcesCitationsAndPersonsReport.
    """
    def __init__(self, name, dbase):
        MenuReportOptions.__init__(self, name, dbase)

        
     
    def add_menu_options(self, menu):
        """ Add the options for this report """
        category_name = _("Report Options")
        
        title = StringOption(_('book|Title'), _('Title of the Book') )
        title.set_help(_("Title string for the book."))
        menu.add_option(category_name, "title", title)
        
        subtitle = StringOption(_('Subtitle'), _('Subtitle of the Book') )
        subtitle.set_help(_("Subtitle string for the book."))
        menu.add_option(category_name, "subtitle", subtitle)
        
        dateinfo = time.localtime(time.time())
        #rname = self.__db.get_researcher().get_name()
        rname = "researcher name"
 
        footer_string = _('Copyright %(year)d %(name)s') % {
            'year' : dateinfo[0], 'name' : rname }
        footer = StringOption(_('Footer'), footer_string )
        footer.set_help(_("Footer string for the page."))
        menu.add_option(category_name, "footer", footer)
        
        # Reload filters to pick any new ones
        CustomFilters = None
        from gramps.gen.filters import CustomFilters, GenericFilter

        opt = FilterOption(_("Select using filter"), 0)
        opt.set_help(_("Select places using a filter"))
        filter_list = []
        filter_list.append(GenericFilter())
        filter_list.extend(CustomFilters.get_filters('Source'))
        opt.set_filters(filter_list)
        menu.add_option(category_name, "filter", opt)
        
        showperson = BooleanOption(_("Show persons"), True)
        showperson.set_help(_("Whether to show events and persons mentioned in the note"))
        menu.add_option(category_name, "showperson", showperson)

    def make_default_style(self, default_style):
        """
        Make the default output style for the Place report.
        """
        self.default_style = default_style
        self.__report_title_style()
        self.__source_title_style()
        self.__source_details_style()
        self.__citation_title_style()
        self.__column_title_style()
        self.__section_style()
        self.__event_table_style()
        self.__details_style()
        self.__cell_style()
        self.__table_column_style()
        self.__index_table_style()
    
    
    def __report_title_style(self):
        """
        Define the style used for the report title
        """
        font = FontStyle()
        font.set(face=FONT_SERIF, size=16, bold=1)
        para = ParagraphStyle()
        para.set_font(font)
        para.set_header_level(1)
        para.set_top_margin(0.25)
        para.set_bottom_margin(0.25)
        para.set_alignment(PARA_ALIGN_CENTER)       
        para.set_description(_('The style used for the title of the report.'))
        self.default_style.add_paragraph_style("SRC-ReportTitle", para)

    def __source_title_style(self):
        """
        Define the style used for the source title
        """
        font = FontStyle()
        font.set(face=FONT_SERIF, size=12, italic=0, bold=1)
        para = ParagraphStyle()
        para.set_font(font)
        para.set_header_level(2)
        para.set(first_indent=0.0, lmargin=0.0)
        para.set_top_margin(0.75)
        para.set_bottom_margin(0.25)        
        para.set_description(_('The style used for source title.'))
        self.default_style.add_paragraph_style("SRC-SourceTitle", para)
        
    def __citation_title_style(self):
        """
        Define the style used for the citation title
        """
        font = FontStyle()
        font.set(face=FONT_SERIF, size=12, italic=0, bold=1)
        para = ParagraphStyle()
        para.set_font(font)
        para.set_header_level(3)
        para.set(first_indent=0.0, lmargin=0.0)
        para.set_top_margin(0.75)
        para.set_bottom_margin(0.0)        
        para.set_description(_('The style used for citation title.'))
        self.default_style.add_paragraph_style("SRC-CitationTitle", para)

    def __source_details_style(self):
        """
        Define the style used for the place details
        """
        font = FontStyle()
        font.set(face=FONT_SERIF, size=10)
        para = ParagraphStyle()
        para.set_font(font)
        para.set(first_indent=0.0, lmargin=0.0)
        para.set_description(_('The style used for Source details.'))
        self.default_style.add_paragraph_style("SRC-SourceDetails", para)

    def __column_title_style(self):
        """
        Define the style used for the event table column title
        """
        font = FontStyle()
        font.set(face=FONT_SERIF, size=10, bold=1)
        para = ParagraphStyle()
        para.set_font(font)
        para.set(first_indent=0.0, lmargin=0.0)
        para.set_description(_('The style used for a column title.'))
        self.default_style.add_paragraph_style("SRC-ColumnTitle", para)

    def __section_style(self):
        """
        Define the style used for each section
        """
        font = FontStyle()
        font.set(face=FONT_SERIF, size=10, italic=0, bold=0)
        para = ParagraphStyle()
        para.set_font(font)
        para.set(first_indent=0.0, lmargin=0.0)

        para.set_top_margin(0.5)
        para.set_bottom_margin(0.25)        
        para.set_description(_('The style used for each section.'))
        self.default_style.add_paragraph_style("SRC-Section", para)

    def __index_table_style(self):
        """
        Define the style used for indext table
        """
        table = TableStyle()
        table.set_width(100)
        table.set_columns(4)
        table.set_column_width(0, 5)
        table.set_column_width(1, 35)
        table.set_column_width(2, 35)
        table.set_column_width(3, 5)
        
        self.default_style.add_table_style("SRC-IndexTable", table)

    def __event_table_style(self):
        """
        Define the style used for event table
        """
        table = TableStyle()
        table.set_width(100)
        table.set_columns(3)
        table.set_column_width(0, 35)
        table.set_column_width(1, 15)
        table.set_column_width(2, 35)

        self.default_style.add_table_style("SRC-EventTable", table)
        table.set_width(100)
        table.set_columns(3)
        table.set_column_width(0, 35)
        table.set_column_width(1, 15)
        table.set_column_width(2, 35)

        self.default_style.add_table_style("SRC-PersonTable", table)

    def __details_style(self):
        """
        Define the style used for person and event details
        """
        font = FontStyle()
        font.set(face=FONT_SERIF, size=10)
        para = ParagraphStyle()
        para.set_font(font)
        para.set_description(_('The style used for event and person details.'))
        self.default_style.add_paragraph_style("PLC-Details", para)

    def __cell_style(self):
        """
        Define the style used for cells in the event table
        """
        cell = TableCellStyle()
        self.default_style.add_cell_style("SRC-Cell", cell)

    def __table_column_style(self):
        """
        Define the style used for event table columns
        """
        cell = TableCellStyle()
        cell.set_bottom_border(1)
        self.default_style.add_cell_style('SRC-TableColumn', cell)

      