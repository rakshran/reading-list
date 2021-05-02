# reading-list
A web-app to automatically update my reading list every day.
-----
**Problem Statement**

I consume short-form content (blogs, news, essays) in two ways -

1. Through emails from my favorite publications and authors
2. By discovering interesting stuff on social media, podcasts or through recommendations and saving the links to [Pocket](https://getpocket.com/). Then going through them at once.

But this was haphazard and I was never satisfied with this approach. There were two problems:

1. If I somehow missed reading the emails when they arrived, they would get lost in my inbox and create clutter. I tried solving for this using labels so that mails pertaining to my reading list get stored in a separate folder. But it was still a mess and the sight of unread emails from the previous day left me full of guilt.
2. The problem with Pocket was that I almost always forgot that I had items saved there. That list also just kept on growing.

**Solution**

I figured I needed an elegant solution to solve this problem. My reading material for the day should lie neatly in one place so that I could scan through everything at once, prioritise based on the time I had at hand and pick the most important stuff for reading. This list should dynamically get updated so that it just stores the reading material that I have received or saved that day.

I built a [web-app](https://www.rakshitranjan.com/reader.html) that does this. Here is how it works:

1. I used AWS-Lambda for my serverless backend to write a program that fetches emails received using the Gmail API and articles added to my Pocket list through the Pocket GET API (both in the last 24 hrs). 
2. The email bodies are saved as html files in a public s3 bucket which gives them their unique urls using which anyone can view those emails.
3. The program combines these email urls with the pocket urls to create a text file with the html code for the body of the webpage. The contents here will be the response of the API call that the client will make to the server for fetching the reading list.
4. I created an API in AWS and exposed it so that I could call it from the client. The client here is my personal website. The API simply returns the html code to be rendered.
5. This way I am able to visit my web-app and see everything that has been added to my reading list in the last 24 hours at one place. It has a clean UI and makes going through things efficient. Also, since it keeps on updating, there is no guilt of having missed anything. I have changed the setting in my email and now the ones belonging to my reading list automatically get archived on arrival and don't create clutter in my inbox.
