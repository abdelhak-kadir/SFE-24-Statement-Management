import csv
import re
from django.shortcuts import get_object_or_404, render
from app import form
from app.form import *
from app.models import *
import PyPDF2
import os
import pandas as pd
from wsgiref.util import FileWrapper
from django.template.response import TemplateResponse
import json
import pdfplumber
from odoo.settings import BASE_DIR
# Create your views here.
import openai
from django.http import  JsonResponse
import json
from django.shortcuts import  redirect , render

openai.api_key = os.environ.get('openai_api_key')

from datetime import datetime

def ask_openai(message):
    user_message = {
        'role': 'user',
        'content': message
    }
    messages = [user_message]
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        max_tokens=150,
        n=1,
        stop=None,
        temperature=0.7
    )
    
    try:
        answer = response['choices'][0]['message']['content'].strip()
        return answer
    except KeyError as e:
        print(f"Error accessing response: {e}")
        return "Error in response format"
    
def chatbot(request):
        if request.method == 'POST':
            message = request.POST.get('message')
            response = ask_openai(message)        
            return JsonResponse({'message': message, 'response': response})
        return render(request, 'chatbot.html',)

def invoice(request):
    response = None  
    
    if request.method == 'POST':
        message = request.POST.get('inv')
        date_filter_form = DateFilterForm(request.POST)
        
        if date_filter_form.is_valid():
            date_value = date_filter_form.cleaned_data['date']
            date_instance, created = Date.objects.get_or_create(date=date_value)
            
            message +="extract from this SMS ('Fournisseur': ,'date': [Date in the format YY/MM/DD, e.g., 24/05/01 for May 1, 2024] ,'amount': [Amount in DH])"
            #message += " - date  - amount  -sevice (extract from this invoice just those 3 infos without any other expression, and return it with this form 'service': Some Service,'date': 2024-05-01,'amount': 100.00 DH), extract amount on DH, and date: yy/mm/dd like 24/01/01 that mean 2024/01/01)"
            
            response = ask_openai(message)
            response_split = response.split(',')
            extract_list = []
            
            for i in response_split:
                extract_list.append(i.split(':'))
            print(extract_list)
            service = extract_list[0][1] 
            date = extract_list[1][1]
            amount = extract_list[2][1][:-2]
            extract = Sms(
                service=service,
                date=date,
                amount=amount,
                date_f=date_instance,
            )
            extract.save()
            
            response = "Sms instance created successfully!"
        else:
            response = "Invalid Date Filter form data!"
    else:
        date_filter_form = DateFilterForm()

    return render(request, 'SMS/inv.html', {'date_filter_form': date_filter_form, 'response': response})

def Releve_Bank(request):
    if request.method == 'POST':
        form = ReleveForm(request.POST, request.FILES)
        date_filter_form = DateFilterForm(request.POST)
        
        if form.is_valid() and date_filter_form.is_valid():
            date_value = date_filter_form.cleaned_data['date']
            date_instance, created = Date.objects.get_or_create(date=date_value)
            
            instance = form.save(commit=False)
            instance.date = date_instance
            instance.save()

            all_text = ""
            with pdfplumber.open(instance.pdf.path) as pdf:
                for page in pdf.pages:
                    text = page.extract_text()
                    lines = text.split('\n')
                    modified_text = '\n'.join(lines[14:-1])
                    all_text += modified_text + '\n\n'

            with open(os.path.join(BASE_DIR, 'txt/extract.txt'), 'w', encoding='utf-8') as text_file:
                text_file.write(all_text)

            with open(os.path.join(BASE_DIR, 'txt/extract.txt'), 'r', encoding='utf-8') as f:
                lines = f.readlines()

            merged_data = []
            start_pattern = r'^(\d{2} \d{2} \d{4}) (\d{2} \d{2} \d{4}) (\d+) (.+?) (\d+,\d{2})?\b$'
            end_pattern = r'^(\d+,\d{2})\+(\d+,\d{2})?$'
            current_transaction = None

            for line in lines:
                line = line.strip()
                start_match = re.match(start_pattern, line)
                if start_match:
                    if current_transaction:
                        merged_data.append(current_transaction)

                    current_transaction = list(start_match.groups())
                    current_transaction[:2] = sorted(current_transaction[:2], key=lambda x: datetime.strptime(x, '%d %m %Y'))
                else:
                    end_match = re.match(end_pattern, line)
                    if end_match and current_transaction:
                        current_transaction.extend(end_match.groups())
                        merged_data.append(current_transaction)
                        current_transaction = None
                    elif current_transaction:
                        current_transaction[3] += ' ' + line

            if current_transaction:
                merged_data.append(current_transaction)

            for data in merged_data:
                Date_operation = datetime.strptime(data[0], '%d %m %Y')
                Date_valeur = datetime.strptime(data[1], '%d %m %Y')
                Reference = data[2]
                Nature_operation = data[3]
                Montant_debit = data[4]
                Montant_credit = data[5] if len(data) > 5 else None

                extract = RELEVE(
                    pdf=instance.pdf.path,
                    date=date_instance,
                    Date_operation=Date_operation,
                    Date_valeur=Date_valeur,
                    Reference=Reference,
                    Nature_operation=Nature_operation,
                    Montant_debit=Montant_debit,
                    Montant_credit=Montant_credit
                )
                extract.save()

            return redirect('filter_releves_by_date')
    else:
        form = ReleveForm()
        date_filter_form = DateFilterForm()

    return render(request, 'Releve/releve.html', {'form': form, 'date_filter_form': date_filter_form})
def upload_pdf_form(request):
    response = None  
    if request.method == 'POST':
        form = PdfFormUploadForm(request.POST, request.FILES)
        date_filter_form = DateFilterForm(request.POST)

        if form.is_valid() and date_filter_form.is_valid():
            date_value = date_filter_form.cleaned_data['date']
            date_instance, created = Date.objects.get_or_create(date=date_value)

            instance = form.save(commit=False)
            instance.date_f = date_instance
            instance.save()

            # Extract text from the uploaded PDF
            try:
                text = ''
                with open(instance.pdf.path, 'rb') as file:
                    reader = PyPDF2.PdfReader(file)
                    for page_num in range(len(reader.pages)):
                        page = reader.pages[page_num]
                        text += page.extract_text()

                processed_text = f"{text}\n  extracte - date  - amount  -service (from this invoive just those 3 infos without any other expression and return it with this form 'service': Some Service,'date': 2024-05-01,'amount': 100.00 USD , EURO ,DH,DHS)"

                response = ask_openai(processed_text)

                response_split = response.split(',')
                extract_list=[]
            
                try:
                    for i in response_split:
                        extract_list.append(i.split(':'))
                    service = extract_list[0][1].strip()
                    date = extract_list[1][1].strip()
                    amount = extract_list[2][1].strip()

                    extract = ExtractedInfo(
                        service=service,
                        date=date,
                        amount=amount,
                        date_f=date_instance
                    )
                    extract.save()
                except Exception as e:
                    print(f"Error processing extracted information: {e}")
                    return render(request, '404.html', {"response": response})

            except Exception as e:
                print(f"Error reading PDF or extracting information: {e}")
                return render(request, '404.html', {"response": response})

            return render(request, 'INVOICE/facture.html', {"response": response})

    else:
        form = PdfFormUploadForm()
        date_filter_form = DateFilterForm()

    return render(request, 'INVOICE/facture.html', {'form': form, 'date_filter_form': date_filter_form})

def save_match(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        releve_id = data.get('releve_id')
        sms_id = data.get('sms_id')
        facture_id = data.get('facture_id')

        try:
            releve = RELEVE.objects.get(id=releve_id)
            sms = Sms.objects.get(id=sms_id) if sms_id else None
            facture = ExtractedInfo.objects.get(id=facture_id) if facture_id else None

            match = Match.objects.create(
                releve=releve,
                sms=sms,
                facture=facture,
                date=releve.date,
                status='Matched'  # Set status here
            )

            return JsonResponse({'success': True})
        except RELEVE.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'RELEVE not found'})
        except Sms.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'SMS not found'})
        except ExtractedInfo.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Facture not found'})
    return JsonResponse({'success': False, 'error': 'Invalid request'})

def Filter_Releves_By_Date(request):
    filtered_releves = []
    sms_list = []
    facture_list = []
    date_filter_form = DateFilterForm(request.GET or None)

    if date_filter_form.is_valid():
        selected_date = date_filter_form.cleaned_data['date']
        month = selected_date.month
        year = selected_date.year

        filtered_releves = RELEVE.objects.filter(date__date__year=year, date__date__month=month).prefetch_related('matches')
        sms_list = Sms.objects.filter(date_f__date__year=year, date_f__date__month=month)
        facture_list = ExtractedInfo.objects.filter(date_f__date__year=year, date_f__date__month=month)

    return render(request, 'filtered_releves.html', {
        'releves': filtered_releves,
        'sms_list': sms_list,
        'date_filter_form': date_filter_form,
        'facture_list': facture_list
    })


def view_matches(request):
    matches = []
    date_filter_form = DateFilterForm(request.GET or None)

    if date_filter_form.is_valid():
        selected_date = date_filter_form.cleaned_data['date']
        month = selected_date.month
        year = selected_date.year

        matches = Match.objects.filter(releve__date__date__year=year, releve__date__date__month=month)

    return render(request, 'view_matches.html', {'date_filter_form': date_filter_form, 'matches': matches})

def update_releve(request, pk):
    releve = get_object_or_404(RELEVE, pk=pk)
    if request.method == 'POST':
        form = ReleveFormUpdate(request.POST, instance=releve)
        if form.is_valid():
            form.save()
            return redirect('filter_releves_by_date')
    else:
        form = ReleveFormUpdate(instance=releve)
    return render(request, 'Releve/releve_form.html', {'form': form})
def update_sms(request, pk):
    sms = get_object_or_404(Sms, pk=pk)
    if request.method == 'POST':
        form = SmsForm(request.POST, instance=sms)
        if form.is_valid():
            form.save()
            return redirect('view_matches')
    else:
        form = SmsForm(instance=sms)
    return render(request, 'SMS/releve_form.html', {'form': form})
def update_inv(request, pk):
    inv = get_object_or_404(ExtractedInfo, pk=pk)
    if request.method == 'POST':
        form = InvoiceFormUpdate(request.POST, instance=inv)
        if form.is_valid():
            form.save()
            return redirect('view_matches')
    else:
        form = InvoiceFormUpdate(instance=inv)
    return render(request, 'INVOICE/releve_form.html', {'form': form})

