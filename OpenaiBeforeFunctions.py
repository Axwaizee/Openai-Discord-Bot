import openai
import datetime

openai.organization = "org-vNmstpCOraNT0PltYS5FPVNy"
openai.api_key = os.environ['APIKEY']
openai.Model.list()


class Conversation:
    def __init__(self):
        self.data = []

    def update_conversation(self, user_id, new_chat):
        for conv in self.data:
            if conv['user_id'] == user_id:
                conv['message'] = new_chat
                conv['time'] = datetime.datetime.now()
                return
        conversation = {'user_id': user_id, 'message': new_chat, 'time': datetime.datetime.now()}
        self.data.append(conversation)

    def get_conversation(self, user_id):
        for conv in self.data:
            if conv['user_id'] == user_id:
                if (datetime.datetime.now() - conv['time']).total_seconds() > 300:
                    self.data.remove(conv)
                    return None
                return conv['message']
        return None


def prompt(message, prev_chat, text):
    user = message.author.name
    bot = message.guild.me.name
    if prev_chat == "" or prev_chat is None:
        return f"The following is a conversation with an AI assistant named {bot} and {user} in discord, the assistant " \
               f"is helpful, creative, clever, and very friendly.\n\n{user}:{text}\n{bot}:"

    elif prev_chat.count("\n") <= 12:
        return prev_chat + f"\n{user}:{text}\n{bot}:"

    elif prev_chat.count("\n") > 12:
        splitted_text = prev_chat.split("\n\n", 1)
        rip_first_chat = splitted_text[1].split("\n", 1)[1]
        return splitted_text[0] + "\n\n" + rip_first_chat + f"\n{user}:{text}\n{bot}:"


def update_message(prev_chat, new_chat):
    if prev_chat:
        return prev_chat + new_chat
    return new_chat


def welcome(member):
    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=f"Just now a member named {member.name} has joined the {member.guild.name} server, welcome them to the server and tell them they can chat with you (you are an AI Discord bot). Replace their name with '{member.mention}'.",
        temperature=0.9,
        max_tokens=150,
        top_p=1,
        frequency_penalty=0.0,
        presence_penalty=0.6
    )

    return response.choices[0].text
