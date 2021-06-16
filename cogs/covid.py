import discord
import os
from discord.ext import commands
import requests
from requests.api import get
import pycountry
import datetime
from datetime import date
import json
import newsapi
from newsapi import NewsApiClient

# covid = Covid()
list_cont = []
class News(commands.Cog):
    def __init__(self,client):
        self.client = client

    def country_list(self):
        country = [(list(pycountry.countries)[i].name, list(pycountry.countries)[i].alpha_2) for i in range(len(pycountry.countries))]
        return country

    def conv(self,num):
        num = str(num)

        x = num[:-3]
        y = num[-3:]
        z = f',{y}'
        for i in range(int(len(x)/2)):
            t = x
            # print(t)
            x = t[:-2]
            y = t[-2:]
            # print(y)
            z = f',{y}{z}'
        if (len(num)) % 2 != 0:
            z = z[1:]
        else:
            z = f'{num[:1]}{z}'

        return z

    def active_cases(self,country):
        # list_cases = covid.get_status_by_country_name(country)
        # print(list_cases)
        d1 = datetime.datetime.now()
        date = d1.strftime("%Y-%m-%d")

        url = "https://covid-193.p.rapidapi.com/history"

        querystring = {"country": country, "day": date}

        headers = {
        'x-rapidapi-key': "d793480370msh89e6757d4f2518cp13872fjsn7f9b392dba12",
            'x-rapidapi-host': "covid-193.p.rapidapi.com"
        }

        response = requests.request(
        "GET", url, headers=headers, params=querystring)

        # print(response.text)
        dataset = (response.text)
        dataset = json.loads(dataset)
        # print(type(dataset))
        content = dataset['response']
        n = len(content)
        if n==1:
            m = 1
        else:
            m = n-1
        list_cases = content[len(content)-1]['cases']
        container = []
        container.append(list_cases['total'])
        container.append(list_cases['active'])
        container.append(list_cases['new'])

        list_deaths = content[len(content)-1]['deaths']
        container.append(list_deaths['total'])
        container.append(list_deaths['new'])
        container.append(content[m]['tests']['total'])
        return container

    @commands.command(aliases=['cinfo','covidinfo'],help='Gives You Covid-19 informations')
    async def _info(self,ctx):
        embed = discord.Embed(
            title='Covid-19', description='Coronavirus disease 2019 (COVID-19), also known as the coronavirus or COVID, is a contagious disease caused by severe acute respiratory syndrome coronavirus 2 (SARS-CoV-2). The first known case was identified in Wuhan, China, in December 2019. The disease has since spread worldwide, leading to an ongoing pandemic.\n for **more info [click here](https://en.wikipedia.org/wiki/COVID-19)**', color=discord.Color.blurple())
        embed.set_thumbnail(
            url="https://innovativegenomics.org/wp-content/uploads/2020/04/Abstract-SARS-CoV-2-in-red-with-RNA.png")
        await ctx.send(embed=embed)
        await ctx.message.add_reaction("👍")

    @commands.command(aliases=['cmed'])
    async def _medicine(self,ctx):
        medurl = "https://www.healthline.com/health/coronavirus-treatment"
        embed = discord.Embed(
            title='General Medicines', description=f'Although you are suggested to get advice from a Doctor\nOne can take these medicines by themselves otherwise !!\n [**know more about medicines**]({medurl})', color=discord.Color.green())

        embed.set_thumbnail(
            url='https://image.flaticon.com/icons/png/512/1098/1098028.png')
        embed.add_field(name="Acidity",value='Pentaprazole 40mg',inline=False)
        embed.add_field(name="Body Pain and Fever",value='Dolo 650mg (for body temp. > 100°F)', inline=False)
        embed.add_field(name="Cough",value='Ambroxyl or Azithromycin 500mg',inline=False)
        embed.add_field(name="Vomitting",value='Ondem 4mg',inline=False)
        embed.add_field(name="Immunity",value='B-C-D vitamins',inline=False)
        await ctx.send(embed=embed)
        await ctx.message.add_reaction("👍")

    @commands.command(aliases=['cases','ccases','cc'])
    async def _cases(self,ctx,*,country='India'):
        await ctx.message.add_reaction("😷")
        arr = self.active_cases(country)
        country = country.capitalize()
        url = f'https://www.google.com/search?q=covid-19+{country}&safe=active'
        embed = discord.Embed(
            title=f'Current Covid-19 cases in {country}',url=url,description=f"Here's the covid stats of **{country}** !",color=discord.Color.blurple())

        embed.add_field(name='Confirmed Cases',value=f'{self.conv(arr[0])}',inline=False)
        embed.add_field(name='Active Cases',value=f'{self.conv(arr[1])}',inline=True)
        embed.add_field(name='New Cases',value=f'+{self.conv(arr[2][1:])}',inline=True)
        embed.add_field(name='Total Deaths',value=f'{self.conv(arr[3])}' ,inline=False)
        embed.add_field(name='New Deaths', value=f'{arr[4]}' , inline=True)
        embed.add_field(name='Total Tested', value=f'{self.conv(arr[5])}' , inline=True)

        await ctx.send(embed=embed)

    @commands.command(aliases=['cvac'])
    async def _vaccine(self,ctx):
        # arr = self.active_cases('india')
        url = 'https://www.mohfw.gov.in/covid_vaccination/vaccination/index.html'
        icmr = 'https://vaccine.icmr.org.in/covid-19-vaccine'
        registration = 'https://www.cowin.gov.in/home'
        embed = discord.Embed(
            title='Vaccination Help', url=url,description='As of now, if your age >= 18 then you must get vaccinated\n more details are given below !',color=ctx.author.color)
        embed.set_thumbnail(
            url='https://images.news18.com/ibnlive/uploads/2021/01/1609996706_co-win-app.jpg')
        embed.add_field(name='Covishield', value='The Serum Institute of India (SII) and Indian Council of Medical Research are jointly conducting a Phase II/III, Observer-Blind, Randomized, Controlled Study to Determine the Safety and Immunogenicity of Covishield (COVID-19 Vaccine).',inline=False)
        embed.add_field(name='Covaxin', value="COVAXIN, India's indigenous COVID-19 vaccine Bharat Biotech is developed in collaboration with the Indian Council of Medical Research(ICMR) - National Institute of Virology(NIV). This indigenous, inactivated vaccine is developed and manufactured in Bharat Biotech's BSL-3 (Bio-Safety Level 3) high containment facility.",inline=False)
        embed.add_field(name='Vaccination Deails',value=f'[**Register for Vaccination**]({registration})',inline=False)
        embed.set_footer(text=f'For more details on Vaccines [click here]({icmr})')

        await ctx.send(embed=embed)
        await ctx.message.add_reaction("🩺")


def setup(client):
    client.add_cog(News(client))
