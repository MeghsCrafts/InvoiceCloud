import csv
import sys
from datetime import datetime

paymentAmounts = {
    'Vitals' : 10,
    'Marriage Intentions' : 25,
    'Business Certificate' : 40,
    'Burial Permit' : 10,
    'Dog RegistrationMF' : 15,
    'Dog RegistrationSN' : 10,
    'Dog Kennel License' : 150,
    'Late Fee (Dog)' : 15,
    'Fine (Dog)' : 50

    }
paymentTypes = {
    # Vitals
    'vitals' : {'category' : 'Vitals', 'price' : paymentAmounts['Vitals']},
    'vital' : {'category' : 'Vitals', 'price' : paymentAmounts['Vitals']},
    'birth certificate' : {'category' : 'Vitals', 'price' : paymentAmounts['Vitals']},
    'birth certificates' : {'category' : 'Vitals', 'price' : paymentAmounts['Vitals']},
    'death certificate' : {'category' : 'Vitals', 'price' : paymentAmounts['Vitals']},
    'death certificates' : {'category' : 'Vitals', 'price' : paymentAmounts['Vitals']},
    'marriage certificate' : {'category' : 'Vitals', 'price' : paymentAmounts['Vitals']},
    # Marriage Intentions
    'marriage intentions' : {'category' : 'Marriage Intentions', 'price' : paymentAmounts['Marriage Intentions']},
    'marriage intention' : {'category' : 'Marriage Intentions', 'price' : paymentAmounts['Marriage Intentions']},
    # Business Certificate
    'business certificate' : {'category' : 'Business Certificate', 'price' : paymentAmounts['Business Certificate']},
    # Burial Permit
    'burial permit' : {'category' : 'Burial Permit', 'price' : paymentAmounts['Burial Permit']},
    # Dogs
    'dog' : {'category' : 'Dog Registration', 'price' : paymentAmounts['Dog RegistrationSN']},
    'dog registration' : {'category' : 'Dog Registration', 'price' : paymentAmounts['Dog RegistrationSN']},
    'male/female' : {'category' : 'Dog Registration', 'price' : paymentAmounts['Dog RegistrationMF']},
    'spayed/neutered' : {'category' : 'Dog Registration', 'price' : paymentAmounts['Dog RegistrationSN']},
    'kennel license' : {'category' : 'Dog Kennel', 'price' : paymentAmounts['Dog Kennel License']},
    'late fee' : {'category' : 'Late Fee (Dog)', 'price' : paymentAmounts['Late Fee (Dog)']},
    'dog late fee' : {'category' : 'Late Fee (Dog)', 'price' : paymentAmounts['Late Fee (Dog)']},
    'dog late fine' : {'category' : 'Fine (Dog)', 'price' : paymentAmounts['Fine (Dog)']},
    # Unknown Transaction
    'unknown transaction' : {'category' : 'Unknown Transaction', 'price' : 0}

}

# Entry Dictionary
# Timestamp - time of transaction
# Payment - amount of payment
# Type - type of payment (dog, vitals, etc)

def PaymentBuilder(payment):
    # Builds the individual payments
    finalPayment = {};
    count = 1;
    type = '';
    if payment[0] == '(':
        payment = payment[1:];
        temp = payment.partition(') ');
        count = int(temp[0]);
    type = temp[2].lower();
    type = type.replace('?', '');
    if type in paymentTypes:
        tempType = paymentTypes.get(type);
        finalPayment['category'] = tempType['category'];
    finalPayment['price'] = paymentTypes[type]['price'] * count;
    return(finalPayment);

def DogDateChecker (date):
    # Returns 0 if the date is before (inclues December) April 1,
    # 1 if the date is after April 1, and 2 if the date is after June 1.
    fullDate = datetime.strptime(date, '%m/%d/%Y %H:%M');
    month = fullDate.month;
    if (((1 <= month) & (month < 4)) | (month == 12)):
        return 0;
    elif (month < 6):
        return 1;
    else:
        return 2;

def AddEntryForDogLateFee(entryList, payment):
    # Add a new entry for a dog late fee, if after 3/31 (last day to register
    # without a late fee).
    entry = {};
    if payment[0] == '(':
        payment = payment[1:];
        temp = payment.partition(') ');
        count = int(temp[0]);
    match DogDateChecker(entryList[-1]['timestamp']):
        case 0:
            return;
        case 1:
            if (entryList[-1]['type'] == 'Dog Registration'):
                entry['timestamp'] = entryList[-1]['timestamp'];
                entry['payment'] = count * paymentAmounts['Late Fee (Dog)'];
                entry['type'] = 'Late Fee (Dog)';
                entryList.append(entry);
        case 2:
            if (entryList[-1]['type'] == 'Dog Registration'):
                entry['timestamp'] = entryList[-1]['timestamp'];
                entry['payment'] = count * paymentAmounts['Late Fee (Dog)'];
                entry['type'] = 'Late Fee (Dog)';
                entryList.append(entry);
                entry['timestamp'] = entryList[-1]['timestamp'];
                entry['payment'] = paymentAmounts['Fine (Dog'];
                entry['type'] = 'Fine (Dog)';
                entryList.append(entry);
    return;                
    

def InternalTransaction(line, entryList, entry):
    # handles payments made in house using "Misc Government Services"
    tempType = line[2].lower();
    if 'type' in entryList[-1]:
        # if this is the second item in a transaction, copy the time stamp
        # from the previous transaction.
        entry['timestamp'] = entryList[-1]['timestamp'];
        entry['payment'] = entryList[-1]['payment'];
        entry['type'] = paymentTypes[tempType]['category'];
        entryList.append(entry);
    else:
        # if this is the first transaction for this entry, it just creates
        # the entry with the payment type and price.
        entry['type'] = paymentTypes[tempType]['category'];
        entryList[-1]['type'] = entry['type'];
        entryList[-1]['payment'] = int(entryList[-1]['payment'])
    return entry;

def ExternalTransaction(line, entryList, entry):
    # Handles payments made online using the consumer side of the website
    if 'type' in entryList[-1]:
        parcedPayment = PaymentBuilder(line[2]);
        entry['timestamp'] = entryList[-1]['timestamp'];
        entry['payment'] = parcedPayment['price'];
        entry['type'] = parcedPayment['category'];
        entryList.append(entry);
        AddEntryForDogLateFee(entryList, line[2])
    else:
        parcedPayment = PaymentBuilder(line[2]);
        entry['payment'] = parcedPayment['price'];
        entry['type'] = parcedPayment['category'];
        entryList[-1]['type'] = entry['type'];
        entryList[-1]['payment'] = entry['payment'];
        AddEntryForDogLateFee(entryList, line[2])

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
                # Handles payments made online using the consumer side of the website
                ExternalTransaction(line, entryList, entry);
            elif line[1] == 'Type of Payment':
                # handles payments made in house using "Misc Government Services"
                InternalTransaction(line, entryList, entry);
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
