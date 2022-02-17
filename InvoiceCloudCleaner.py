import csv
import sys

paymentAmounts = {
    'Vitals' : 10,
    'Marriage Intentions' : 25,
    'Business Certificate' : 40,
    'Burial Permit' : 10,
    'Dog Registration' : 10,
    'Dog RegistrationMF' : 15,
    'Dog RegistrationSN' : 10
    }
paymentTypes = {
    'vitals' : {'category' : 'Vitals', 'price' : paymentAmounts['Vitals']},
    'birth certificate' : {'category' : 'Vitals', 'price' : paymentAmounts['Vitals']},
    'death certificate' : {'category' : 'Vitals', 'price' : paymentAmounts['Vitals']},
    'marriage certificate' : {'category' : 'Vitals', 'price' : paymentAmounts['Vitals']},
    'marriage intention' : {'category' : 'Marriage Intentions', 'price' : paymentAmounts['Marriage Intentions']},
    'business certificate' : {'category' : 'Business Certificate', 'price' : paymentAmounts['Business Certificate']},
    'burial permit' : {'category' : 'Burial Permit', 'price' : paymentAmounts['Burial Permit']},
    'dog registration' : {'category' : 'Dog Registration', 'price' : paymentAmounts['Dog Registration']},
    'male/female' : {'category' : 'Dog Registration', 'price' : paymentAmounts['Dog RegistrationMF']},
    'spayed/neutered' : {'category' : 'Dog Registration', 'price' : paymentAmounts['Dog RegistrationSN']}
}

def PaymentBuilder(payment):

    finalPayment = {};
    count = 1;
    type = '';
    if payment[0] == '(':
        count = int(payment[1])
        temp = payment.partition(') ');
    type = temp[2].lower();
    type = type.replace('?', '');
    if type[-1] == 's':
        type = type[:-1];
    if type in paymentTypes:
        tempType = paymentTypes.get(type);
        finalPayment['category'] = tempType['category'];
    finalPayment['price'] = paymentTypes[type]['price'] * count;
    return(finalPayment);


def BuildEntryList():
    entryList=[];
    with open(sys.argv[1]) as sourceFile:
        sourceData = csv.reader (sourceFile, delimiter=',')
        for line in sourceData:
            entry={};
            if line[0] != '':
                entry['timestamp'] = line[0];
                entry['payment'] = line[2];
                entryList.append(entry);
            elif line[1] == 'Item':
                if 'type' in entryList[-1]:
                    parcedPayment = PaymentBuilder(line[2]);
                    entry['timestamp'] = entryList[-1]['timestamp'];
                    entry['payment'] = parcedPayment['price'];
                    entry['type'] = parcedPayment['category'];
                    entryList.append(entry);
                else:
                    parcedPayment = PaymentBuilder(line[2]);
                    entry['payment'] = parcedPayment['price'];
                    entry['type'] = parcedPayment['category'];
                    entryList[-1]['type'] = entry['type'];
                    entryList[-1]['payment'] = entry['payment'];
            elif line[1] == 'Type of Payment':
                tempType = line[2].lower();
                if 'type' in entryList[-1]:
                    entry['timestamp'] = entryList[-1]['timestamp'];
                    entry['payment'] = entryList[-1]['payment'];
                    entry['type'] = paymentTypes[tempType]['category'];
                    entryList.append(entry);
                else:
                    entry['type'] = paymentTypes[tempType]['category'];
                    entryList[-1]['type'] = entry['type'];
                entryList[-1]['payment'] = int(entryList[-1]['payment'])
        sourceFile.close();
    return(entryList);

def PrintEntryList():
    midList=BuildEntryList();
    finalForm = [];
    for line in midList:
        entry = list(line.values());
        finalForm.append(entry);
    fields = ['Timestamp', 'Payment', 'Type'];

    with open ('results.csv', 'w') as file:
        write = csv.writer(file);
        write.writerow(fields);
        write.writerows(finalForm);
    return(finalForm);


PrintEntryList()


