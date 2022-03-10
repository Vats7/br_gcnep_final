from django.forms import DateTimeInput


class XDSoftDateTimePickerInput(DateTimeInput):
    template_name = 'lms/widgets/xdsoft_datetimepicker.html'
