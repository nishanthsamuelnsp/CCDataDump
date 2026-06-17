from shared.defaults_service import load_defaults


MODULE_KEY = "dwc"


def get_dwc_entry_sections():
    defaults = load_defaults()
    return {
        "handling": defaults["dwc"]["handling"],
        "dispatch": defaults["dwc"]["dispatch"],
    }
