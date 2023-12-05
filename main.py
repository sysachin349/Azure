import asyncio
import configparser
from msgraph.generated.models.o_data_errors.o_data_error import ODataError
from graph import Graph
import requests
import time




async def main():
    print('Python Graph \n')
    try:
        response = requests.get('https://httpbin.org/ip')
        ip_data = response.json()
        if not ip_data["origin"] == "115.113.213.2":
            print("Exception in logging!")
            exit()
    except Exception as e:
        print("Exception in logging!")
        exit()


    # Load settings
    config = configparser.ConfigParser()
    config.read(['config.cfg', 'config.dev.cfg'])
    azure_settings = config['azure']

    graph: Graph = Graph(azure_settings)

    user = await greet_user(graph)

    choice = -1

    while choice != 0:
        print('Please choose one of the following options:')
        print('0. Exit')
        print('1. Display access token')
        print('2. List my inbox')
        print('3. Send mail')
        print('4. Make a Graph call')

        try:
            choice = int(input())
        except ValueError:
            choice = -1

        try:
            if choice == 0:
                print('Goodbye...')
            elif choice == 1:
                await display_access_token(graph)
            elif choice == 2:
                await list_inbox(graph)
            elif choice == 3:
                await send_mail(graph)
            elif choice == 4:
                await make_graph_call(graph)
            else:
                print('Invalid choice!\n')
        except Exception as odata_error:
            print('Error:')
            if odata_error.error:
                print(odata_error.error.code, odata_error.error.message)

async def greet_user(graph: Graph):
    user = await graph.get_user()
    if user:
        print('Hello,', user.display_name)
        # For Work/school accounts, email is in mail property
        # Personal accounts, email is in userPrincipalName
        print('Email:', user.mail or user.user_principal_name, '\n')
        return user

async def display_access_token(graph: Graph):
    token = await graph.get_user_token()
    print('User token:', token, '\n')

    
async def list_inbox(graph: Graph):
    message_page = await graph.get_inbox()
    if message_page and message_page.value:
        # Output each message's details
        for message in message_page.value:
            print('Message:', message.subject)
            if (
                message.from_ and
                message.from_.email_address
            ):
                print('  From:', message.from_.email_address.name or 'NONE')
            else:
                print('  From: NONE')
            print('  Status:', 'Read' if message.is_read else 'Unread')
            print('  Received:', message.received_date_time)

        # If @odata.nextLink is present
        more_available = message_page.odata_next_link is not None
        print('\nMore messages available?', more_available, '\n')


async def send_mail(graph: Graph):
    counter=0
    user = await graph.get_user()
    if user:
        try:
            with open('emailBody.txt', 'r') as file:
                emailBody=file.read()
        except FileNotFoundError:
            print("Emailbody file not found!")
        except Exception as e:
            print(e)
        # Send mail to the signed-in user
        # Get the user for their email address
        try:
            with open('emailList.txt','r') as file:
                for Email in file:
                    await graph.send_mail('Testing Microsoft Graph', emailBody, Email.strip() or '')
                    with open('log.txt', 'a') as file:
                        file.write(f'Email send to {Email} !')
                        counter += 1
                        if counter == 30:
                            time.sleep(60)
                            print('Sleeping for one min!!!!')
                            counter = 0
        except FileNotFoundError:
            print(f"Error: File emailList.txt not found.")
        except Exception as e:
            print(f"Error: {e}")

async def make_graph_call(graph: Graph):
    await graph.make_graph_call()


# Run main
asyncio.run(main())