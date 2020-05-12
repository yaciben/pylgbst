class EnglishNumbers:
    num2words1 = {1: 'One', 2: 'Two', 3: 'Three', 4: 'Four', 5: 'Five',
                  6: 'Six', 7: 'Seven', 8: 'Eight', 9: 'Nine', 10: 'Ten',
                  11: 'Eleven', 12: 'Twelve', 13: 'Thirteen', 14: 'Fourteen',
                  15: 'Fifteen', 16: 'Sixteen', 17: 'Seventeen', 18: 'Eighteen', 19: 'Nineteen'}
    num2words2 = ['Twenty', 'Thirty', 'Forty', 'Fifty', 'Sixty', 'Seventy', 'Eighty', 'Ninety']

    def number(self, number):
        if 0 <= number <= 19:
            return self.num2words1[number]
        elif 20 <= number <= 99:
            tens, remainder = divmod(number, 10)
            return self.num2words2[tens - 2] + '-' + self.num2words1[remainder] if remainder else self.num2words2[tens - 2]
        else:
            print('Number out of implemented range of numbers.')


class FrenchNumbers:
    num2words1 = {1: 'Un', 2: 'Deux', 3: 'Trois', 4: 'Quatre', 5: 'Cinq',
                  6: 'Six', 7: 'Sept', 8: 'Huit', 9: 'Neuf', 10: 'Dix',
                  11: 'Onze', 12: 'Douze', 13: 'Treize', 14: 'Quatorze',
                  15: 'Quinze', 16: 'Seize', 17: 'Dix-Sept', 18: 'Dix-Huit', 19: 'Dix-Neuf'}
    num2words2 = ['Vingt', 'Trente', 'Quarante', 'Cinquante']
    num2words3 = ['Soixante']
    num2words4 = ['Quatre-vingt']

    def number(self, Number):
        if 0 <= Number <= 19:
            return self.num2words1[Number]
        elif 20 <= Number <= 59:
            tens, remainder = divmod(Number, 10)
            return self.num2words2[tens - 2] + ('-et' if remainder is 1 else '') + ('-' + self.num2words1[remainder] if remainder else '')
        elif 60 <= Number <= 79:
            tens, remainder = divmod(Number, 20)
            return self.num2words3[0] + ('-et' if remainder in [1, 11] else '') + ('-' + self.num2words1[remainder] if remainder else '')
        elif 80 <= Number <= 99:
            tens, remainder = divmod(Number, 20)
            return self.num2words4[0] + ('-' + self.num2words1[remainder] if remainder else '')
        else:
            print('Number out of implemented range of numbers.')


if __name__ == '__main__':
    english_numbers = EnglishNumbers()
    french_numbers = FrenchNumbers()
    for i in range(1, 100):
        en = english_numbers.number(i).lower()
        fr = french_numbers.number(i).lower()
        print("{},{},{},".format(i, en, fr))

