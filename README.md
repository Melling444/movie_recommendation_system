# movie_recommendation_system
End-to-End movie recommendation system built on a web-scraped database from rotten tomatoes

To start the project, simply clone the github repository and, assuming you have docker desktop installed, navigate to the folder "movie_recommendation_project" and run a docker-compose up --build in the command line. Then, navigate to http://localhost:3000/ in the web browser to use the recommender.

![image](https://github.com/user-attachments/assets/1d73346a-0e49-4606-8cf7-f2872de8ca0e)

![image](https://github.com/user-attachments/assets/03c09d85-07c0-4720-a9ff-56d0ebc4b174)

I started this project a couple of months ago as I was looking to tackle a project where I had to collect my own data and opted on media recommendations. I initially looked into movies and realized that imdb and rotten tomatoes did not publically share the underlying database that they utilize to display all of the publically available information on the movies listed. That led me down a rabbit hole of learning to build a web-scraper using selenium and optimize it to access a large number of web pages to scrape as much information as possible. I then preprocessed the data into a usuable dataframe. I opted to use a cosine similarity matrix to build the recommendation system, as I was limited to item-based collaboration without a large database of user recommendations (it seems like you can access that on rotten tomatoes but not without being computationally and time intensive on the web scraper). I also wanted to implement a method of sorting scoring based on a list of movies, rather than just a single entry. I opted on taking a set number of high scoring similar movies for each movie in the list, sorting out the duplicates and ordering them by their similarity score. While maybe not intuitive, this should show the highest similarities to those movies referenced in the list without having to add additional mass to the matrix (ngrams, for instance, could be another approach).  

This was also my first time ever using java and I decided that I wanted to have a nice (it's not nice, but it works...) user interface for the recommendation system. I dove into learning as much java, html, and css as I could in order to build a locally hosted web app for the project and while I am proud of what I ended up with, there is much to do for improvements.

I did not end up using all of the information I collected (and there is certainly more that I could do to further optimize the recommendation system) so there is more work to be done and I will do more down the road.

Another big limitation with this project, currently, is the amount of data I have in my database from rotten tomatoes. I am planning on broadaning the scope of my web scraper such that I improve on the amount of movies that I am able to compare from, not just those that are new releases. That should be updated soon (hopefully)!

