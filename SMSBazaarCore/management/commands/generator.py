from django.core.management.base import BaseCommand, CommandError
from SMSBazaarCore.models import Scratch
from SMSBazaarCore.bankcalls import GenerateScratchCardCode


class Command(BaseCommand):
    def handle(self, *args,**options):
        print("amount: ")
        ScratchAmount = input()
        print("Number of codes to generate: ")
        num = input()


        while num > 0:
            ScratchCode = GenerateScratchCardCode()
            try:
                s = Scratch.objects.get(pk=ScratchCode)
            except Scratch.DoesNotExist:
                s = Scratch(code=ScratchCode, amount=int(ScratchAmount))
                s.save()
                num -= 1
