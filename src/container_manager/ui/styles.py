#===============================================================================

import ttkbootstrap as ttk
import ttkbootstrap.constants as constants

#===============================================================================

LEFT_LINK_BUTTON_LABEL = 'LeftLink.Link.TButton'

def initialise_styles(app):
    # A left aligned button label
    app.style.configure(LEFT_LINK_BUTTON_LABEL, anchor=constants.W)

#===============================================================================
