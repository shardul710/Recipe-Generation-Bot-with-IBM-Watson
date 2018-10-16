'''

@author Saurabh Parekh
@author Shardul Dabholkar
@author Aishwariya Desai


The program perform to part. Once is to connect the bluemix and slack bot to python. While the bluemix conversation is
the heart of the entire conversation the
'''
from operator import itemgetter
import random
import time
from slackclient import SlackClient
from cloudant.client import Cloudant
from watson_developer_cloud import ConversationV1
from nltk.stem import WordNetLemmatizer


state={}
userstate={}
conversation_context={}
likes=[] #it stores the the ingridients the person is requesting or likes in hi/her meal
dislikes=[]#it things person doesnot like in their dish.

BOT_NAME = 'chef' # name of the idm bot
#BOT_NAME = 'IBM Watson Conversation'
slack_client = SlackClient('xoxb-274716431700-mXPpYsG8mRN6LMD3ZM3YYgaX') # this one is for the chef




# a global dicitinoary to classify the ingridients in different category like fruit, vegetable etc

all_ingrident_action={
    "almond":"fruit",
    "amaretto":"drink",
    "anchovy":"meat",
    "anise":"spice",
    "anthony bourdain":"",
    "aperitif":"drink",
    "apple":"fruit",
    "apple juice":"drink",
    "apricot":"fruit",
    "artichoke":"vegetable",
    "arugula":"vegetable",
    "asian pear":"fruit",
    "asparagus":"vegetable",
    "aspen":"spice",
    "avocado":"fruit",
    "bacon":"meat",
    "banana":"fruit",
    "basil":"vegetable",
    "bass":"meat",
    "bastille":"fruit",
    "bean":"pulse",
    "beef":"meat",
    "beer":"drink",
    "beat":"vegetable",
    "bitters":"drink",
    "blackberry":"fruit",
    "blue cheese":"cheese",
    "blueberry":"fruit",
    "bok chaoy":"vegetable",
    "bourbon":"drink",
    "bran":"grain",
    "brandy":"drink",
    "bread crumb":"dressing",
    "brie":"cheese",
    "brine":"drink",
    "brisket":"meat",
    "tomato":"vegetable",
    "onion":"vegetable",
    "broccoli":"vegetable",
    "cucumber":"vegetable",
    "cabbage":"vegetable",
    "caauliflower":"vegetable",
    "carrot":"vegetable",
    "eggplant":"vegetable",
    "mango":"fruit",
    "guava":"fruit",
    "kiwi":"fruit",
    "lichi":"fruit",
    "melon":"fruit",
    "papaya":"fruit",
    "pear":"fruit",
    "pineapple":"fruit",
    "pomegrante":"fruit",
    "rasberry":"fruit",
    "mushroom":"vegetable",
    "ginger":"spice",
    "chicken":"meat",
    "goat":"meat",
    "lamb":"meat",
    "pork":"meat",
    "sausage":"meat",
    "rabbit":"meat",
    "deer":"meat",
    "octopus":"meat",
    "steak":"meat",
    "squid":"meat",
    "turkey":"meat",
    "fish":"meat",
    "chili":"spices",
    "garlic":"spice",
    "cheese":"cheese",
    "asiago":"cheese",
    "cheddar":"cheese",
    "blue cheese":"cheese",
    "feta":"cheese"
}

#action- This dictinoary provides the action that needs to be performed on the obtained ingridient.

actions ={
    "vegetable":["chop","slice","dice","brunoice","julienne"],
    "meat":["mince","chop","cut","fry","bake"],
    "fruit":["chop","slice","cut","liquidify","blend"],
    "spices":["grind","add","chop","saute","pan fry"],
    "drink":["add","mix","pour","blend","mix"],
    "cheese":["grate","melt","shred","add","sprinkle"],
    "pulse":["boil","grind","liquidify","heat","fry"]
}


def get_ingridients():

    '''

    :return:the list of ingredient

    The function finds ingredients that needs to be included in the recipe.
    Not all ingridients are completely unique but you will be hearing a group of ingredient that might not be used
    together.
    '''

    global actions, all_ingrident_action,likes,dislikes

    ingridients={}
    recipe={}

    ingridient_list=[]

    # creating a look up table to point the index of the ingridient to the to ingridient. So key will be the index
    # and value will be name of ingridient.
    with open("input.csv") as myfile:
        for lines in myfile:
            line= lines.strip().split(',')
            for item in range(6,len(line)):
                key=item
                value=line[item]
                ingridients[key]=value
            break

    print(ingridients)

    #creating second dictionary, which as recipe as key and ingridients values
    with open("input.csv", encoding="utf8") as myfile:
        flag=False
        for lines in myfile:
            if flag==False:
                flag= True
            else:
                value=[]
                line=lines.strip().split(',')
                #print(line)
                key=line[0]
                for items in range(6,len(line)):
                    if line[items] =='1':
                        val=ingridients.get(items)
                        value.append(val)
            recipe[key]=value

    #print(recipe) #dictinoary tells which recipe has which ingridients

    #creating third dictionary, which has ingridient as key and all the ingridient in which it is occuring as values
    #the with condition takes the input into the list and succesive for loop creats the dictionry
    with open("input.csv", encoding="utf8") as myfile:
        flag= False

        for lines in myfile:
            line=lines.strip().split(',')


            ingridient_list.append(line)



    ingridients_to_recipe={}
    print(len(ingridient_list))


    for coloumn in range (6,len(ingridient_list[0])):
        key=ingridient_list[0][coloumn]
        value=[]
        for row in range(1,20047): #number of recipes in our input data

            if ingridient_list[row][coloumn]=='1':
                var=ingridient_list[row][0]
                value.append(var)
        ingridients_to_recipe[key]=value
    print(ingridients_to_recipe)


    #this is the heart of the algorithm for finding different ingridients
    different_ingridients=[]
    # for evry item in the like list perform this alforithm
    for items in likes:
        temp=[items]
        number_of_iteration=0

        #we will find 5 items for each ingrident in the like list.
        #note that not all 5 ingridients are associated with one ingridient.
        #only the first one is directly associated with the first ingrident  in the like list the next ingridient
        #  is third ingridient is obtained from the second, 4th from 3rd and 5th from 4th
        while number_of_iteration!=5:
            recipies=ingridients_to_recipe.get(temp[number_of_iteration]) #get all the recipe from the current_ingrident in consideration
            counter={}      #the counter will keep count of each and evry ingridient which has occured with the current
                            #ingrident in some recipe
            temp_ingridient = []

            # for all the recipes in which the current_ingridient occured do the following
            for values in recipies:
                #find all the ingridient in that recipe and then increment the count
                per_ingridient=recipe.get(values)
                for count in per_ingridient:
                    if counter.get(count)!=None:
                        value=counter.get(count)
                        value[1]=value[1]+1
                        counter[count]=value
                    else:
                        value=[count,1]
                        counter[count]=value

            #converting dictionary to list. its a 2d list where 0th value is a the ingridient and 1th value of
            # the indgrient is the count.
            for keys in counter:

                temp_ingridient.append(counter.get(keys))
            temp_ingridient=sorted(temp_ingridient,key=itemgetter(1),reverse=True) #sorting based on the count
            total=temp_ingridient[0][1]
            for i in range (len(temp_ingridient)):
                confidence=temp_ingridient[i][1]/total #calculating the confidence score
                #selecting the ingridient between 0.1 to 0.7 - we selected this range because this is when we start
                #geting ingridnets that do not occur often with the selected ingrident.
                if confidence<(random.uniform(0.1,0.07)) and temp_ingridient[i][0] not in temp:
                    temp.append(temp_ingridient[i][0])
                    number_of_iteration+=1
                    break

        #from all_ingrident list we find the category to which the food item belongd and assign particular value to it.
        different_ingridients.append(temp)
        str=""
        for stuffs in (different_ingridients):

            for category in stuffs:

                if category in all_ingrident_action:

                    var=all_ingrident_action.get(category)
                    action=actions.get(var)


                    randon_num=random.randint(0,4)
                    action_var=action[randon_num]
                    str=str+action_var+" "+"the "+category+"\n"
                else:
                    str=str+"add the "+category+"\n"

    print(str)


    return str





def post_to_slack(response, channel):

    '''
    The function is responsible for positing the response obtained from bluemix to post to slack bot.
    :param response:
    :param channel:
    :return: None
    '''
    global  slack_client,likes, dislikes
    slack_client.api_call("chat.postMessage", channel=channel, text=response, as_user=True)





def handle_message(meassage,meassage_sender, channel,conversation_client,conversation_workspace_id):

    '''
    This the flow between the bluemix and the python. The function will identify the ingridient and then responf according
    to the identified itent.
    :param meassage:
    :param meassage_sender:
    :param channel:
    :param conversation_client:
    :param conversation_workspace_id:
    :return: None
    '''

    global state,userstate, conversation_context
    response=" "
    if message_sender in userstate:
        state_current = userstate[message_sender]
    else:
        state_current="Grettings"
        userstate[message_sender] = state_current
    watson_response = conversation_client.message( #its call to the watson's bluemix conversation api and receving the response accordingly
        workspace_id= conversation_workspace_id,
        message_input={'text': message},
        context=conversation_context
    )
    print("context",watson_response['context'])
    print("intent", watson_response['intents'])
    print("entites", watson_response['entities'])
    intents= watson_response['intents']
    entites=watson_response['entities']
    dict_intent=intents[0]


    conversation_context = watson_response['context']
    print(dict_intent['intent'])=='greetings'
    if dict_intent['intent']=='greetings': #if the intent is greeting then execute following condition
         #print("I came here")
         for text in watson_response['output']['text']:
             response += text + "\n"
         print('response',response)
         conversation_context = watson_response['context']

    elif dict_intent['intent']=='myIngredients': #if the intent is myingridient then execute the following condition

        for text in watson_response['output']['text']:
            response += text + "\n"

        #appending the item to the kijes
        for item in entites:

            #print("item",item)
            vars=item['value']
            lemmatizer = WordNetLemmatizer()
            lemmatizer.lemmatize(vars)   #lemmatizing the words so that if handle the pular values
            likes.append(vars)
        #print(likes)
        print('response', response)
    elif dict_intent['intent']=='AvoidUsing':

        for text in watson_response['output']['text']:
            response += text + "\n"

        #appending dislikes
        for item in entites:
            vars = item['value']
            lemmatizer = WordNetLemmatizer()
            lemmatizer.lemmatize(vars)
            dislikes.append(item['value'])

        #print(dislikes)
        print('response', response)

    elif dict_intent['intent']=='afterAvoid': #once you get the response of the after avoid execute the following loop

        for text in watson_response['output']['text']:
            response += text + "\n"

        output=get_ingridients() #generate the ingridient.
        response += output

    else :
        for text in watson_response['output']['text']:

            response += text + "\n"
        conversation_context = watson_response['context']
        print(conversation_context)

        print('response', response)
    post_to_slack(response,channel)




def parse_output(slack_output, conversation_client, conversation_work_shape_id):
    '''

    :param slack_output:
    :param conversation_client:
    :param conversation_work_shape_id:
    :return: text, user and channel
    the function provides the user to which the output is directed and the channel of the user.
    This part of the code is reffered from: watson-recipe-bot-nodejs-janusgraph project
    '''

    if slack_output and len(slack_output)>0:

        for outputs in slack_output:
            if outputs and 'text' in outputs and 'user_profile' not in outputs and atbot in outputs['text']:
                return outputs['text'].split(atbot)[1].strip().lower(), outputs['user'], outputs['channel']
            elif outputs and 'text' in outputs and 'user_profile' not in outputs:
                return outputs['text'].lower(), outputs['user'], outputs['channel']
    return None, None, None



if __name__ == "__main__":
  '''
  the main function does all the connection between python and the bluemix 
  this part of the code was refered from this: watson-recipe-bot-nodejs-janusgraph project
  '''
  api_call = slack_client.api_call("users.list")
  if api_call.get('ok'):
    # retrieve all users so we can find our bot
    users = api_call.get('members')
    for user in users:
      if 'name' in user and user.get('name') == BOT_NAME:
        bot_id=user.get('id')
        atbot ="<@" + bot_id + ">:"
        print("Bot ID for '" + user['name'] + "' is " + user.get('id'))
  else:
    print("could not find " + BOT_NAME)

  #these credentials are necessary for the connecting to the bluemix conversation api.
  bluemix_username="ef5bf17f-2453-4fa3-99f7-be2fd0e7ee28"
  bluemix_password="LZsJCin1pS2L"
  conversation_work_shape_id="75b64e8b-f573-4ae3-b569-e2f6cef4e231"
  conversation_client = ConversationV1(
      username=bluemix_username,
      password=bluemix_password,
      version='2016-07-11'
  )
  #print(conversation_client)

  #the for loop keeps on going untill we stop it manually
  while(True):
      if slack_client.rtm_connect():
          print("connection is established")
          while(True):
              slack_output = slack_client.rtm_read()


              message, message_sender, channel = parse_output(slack_output, conversation_client,conversation_work_shape_id)

              if message and channel and message_sender != bot_id:
                handle_message(message, message_sender, channel,conversation_client,conversation_work_shape_id)

          break
