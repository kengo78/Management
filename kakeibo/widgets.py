from django import forms

class RadioSelect(forms.RadioSelect):
    template_name = 'kakeibo/widgets/custom_radio.html'
    option_template_name = 'kakeibo/widgets/custom_radio_options.html'
    
    def __init__(self, attrs=None):
        super().__init__(attrs)
        if 'class' in self.attrs:
            self.attrs['class'] += ' custom-radio'
        else:
            self.attrs['class'] = 'custom-radio'