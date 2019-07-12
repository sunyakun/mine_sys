from django.dispatch import Signal

on_dataset_finish = Signal(providing_args=['name', 'models', 'predict'])
on_exception_occur = Signal(providing_args=['name', 'exception'])
