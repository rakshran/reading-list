# reading-list
A web-app to automate my reading material for the day.
-----
**Problem Statement**

I consume content in two ways -

1. Subscribing to emails from my favorite publications and authors
2. Coming across good recommended posts on Social Media or Personal Networks

Here are the problems that I faced with the two ways:

1. If I somehow missed reading them when they arrived, they would get lost in the pile of emails and create clutter. I tried solving for this using labels so that mails pertaining to my reading list get stored in a separate folder. But it was still a mess and the sight of unread emails from the previous day left me full of guilt.
2. I used to save these posts using [Pocket](https://getpocket.com/) so that I could get to them in my free time. But I almost always forgot that I had items saved there.

**Solution**

I built a [web-app](https://www.rakshitranjan.com/reader.html) to solve this problem. Here is how it works:

1. I used AWS-Lambda for my serverless backend to write a program that fetches emails received using the Gmail API and articles added to my Pocket list through the Pocket GET API (both in the last 24 hrs). 
2. The email bodies are saved as html files in a public s3 bucket which gives them their unique urls using which anyone can view those emails.
3. The program combines these email urls with the pocket urls to create a text file with the html code for the body. The contents here will be the response of the API call that the client will make to the server for fetching the reading list.
4. I created an API in AWS and exposed it so that I could call it from the client. This API simply returns the html code to be rendered.
5. This way I am able to visit my web-app and see everything that has been added to my reading list in the last 24 hours at one place through a clean UI. Since it keeps on updating, there is no guilt of having missed anything. My email is still there in the inbox but it automatically gets archived on arrival so it doesn't create clutter.
