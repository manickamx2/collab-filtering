# Manickam Manickam
# recommend.py - implementation of collaborative filtering

import sys
import math
from operator import itemgetter

##### GET ALL ARTISTS FROM BOTH SETS OF DATA #####
def getArtists(data, all_artists):
    data = iter(data)
    next(data) # skip the first line 'User, Artist, Plays'
    for line in data:
        line = line.strip().split(",")
        artist = line[1]
        if artist not in all_artists:
            all_artists.append(artist)

    return all_artists

##### PROCESS DATA INTO INSTANCES, APPEND INSTANCE INTO ITS APPROPRIATE SET #####
def process(data, all_artists, instanceSet):
    data = iter(data)
    next(data) # skip the first line 'User, Artist, Plays'
    for line in data:
        line = line.strip().split(",")
        user = line[0]
        artist = line[1]
        plays = int(line[2])
        if user not in instanceSet:
            instance = {}  # represent an instance as a dictionary. keys = artists, values = plays.
            for a in all_artists:
                instance[a] = None  # loop through list of all artists, pre-populate instance w/ all artists and no plays.

            instance[artist] = plays
            instanceSet[user] = instance
        else:
            instanceSet[user][artist] = plays

##### SIMILARITY FUNCTION #####
# returns a similarity rating between two users.
def similarityFunction(user, other_user):
    numerator = 0.0 # NUMERATOR - for each shared artist between two users, multiply each user's rating of that artist together and sum.
    # denominator = 0.0 # DENOMINATOR - square root of the sum of all artist ratings squared, multiply each user's sums together.
    left = 0.0
    right = 0.0

    for (a,r), (a2,r2) in zip(user.items(), other_user.items()):
        if r is not None and r2 is not None: # meaning if both users have rated that artist...
            numerator += r * r2
            left += r**2 # rating of artist a squared
            right += r2**2 # rating of artist a2 squared
        else: # meaning one or both users have not rated that artist...
            numerator += 0
            if r is not None and r2 is None: # still, if a had RATING but a2 didn't...
                left += r**2
            if r2 is not None and r is None: # same as above, vice-versa...
                right += r2**2
    denominator = math.sqrt(left) * math.sqrt(right)

    # return the quotient (similarity rating of two users)
    if denominator == 0.0:
        return denominator
    else:
        return numerator/denominator

##### AVERAGE RATING (OPTION 1) #####
# 'users' parameter passes info containing each user and their top 3 users most similar to them.
# otherUsers[user[1][i][0]] contains the i most similar users indexed via similarity list within 'users'.
def averageRating(user, otherUsers, recUsers): # using k = 3
    ratings_list = []
    for a,r in recUsers[user[0]].items():
        if r is None: # if the artist is not rated...
            total_rating = 0.0 # total rating for the unrated artist.
            count = 0
            for i in range(3): # loop through the top 3 most similar users
                r2 = otherUsers[user[1][i][0]][a] # the other user's rating of artist a.
                if r2 is not None:
                    total_rating += r2
                    count += 1
                else:
                    continue # if the artist is not rated then ignore it.
            avg_rating = 0.0
            if count != 0:
                avg_rating = total_rating / count # average rating
            tup = (a, avg_rating) # a tuple containing the artist and their calculated avg. rating.
            ratings_list.append(tup)
        else: # if the artist is already rated just continue
            continue

    # sort rating list
    ratings_list = sorted(ratings_list, key = itemgetter(1), reverse = True)
    return ratings_list # a list of average ratings of all artists which user p has not listened to

##### WEIGHTED AVERAGE RATING (OPTION 2) #####
def weightedAverageRating(user, otherUsers):
    ratings_list = []
    # calculate z, the sum of all similarity ratings between user p and each other user from otherUsers.
    z = 0.0
    for other_user in otherUsers:
        z += similarityFunction(user, otherUsers[other_user])

    for a,r in user.items():
        if r is None: # if the user P has not rated artist a...
            rating = 0.0
            for other_user in otherUsers: # loop through each user in otherUsers
                r2 = otherUsers[other_user][a] # the other user's rating of artist a
                if r2 is not None: # if the other user HAS rated artist a
                    to_add = similarityFunction(user, otherUsers[other_user]) * r2
                    rating += to_add
                else:
                    continue
            if z != 0.0: # don't want to divide by zero
                weighted_rating = rating / z
            else:
                weighted_rating = 0.0
            tup = (a, weighted_rating)
            ratings_list.append(tup)
        else:
            continue

    # sort rating list
    ratings_list = sorted(ratings_list, key=itemgetter(1), reverse=True)
    return ratings_list

##### ADJUSTED WEIGHTED AVERAGE RATING (OPTION 3) #####
def adjustedWeightedAverageRating(user, otherUsers):
    ratings_list = []
    # calculate z, the sum of all similarity ratings between user p and each other user from otherUsers.
    z = 0.0
    for other_user in otherUsers:
        z += similarityFunction(user, otherUsers[other_user])

    # define average rating function
    def avg_rating(user_p):
        rating = 0
        count = 0
        for r in user_p.values():
            if r is not None:
                count += 1
                rating += r
        avg_rating = rating / count
        return avg_rating

    user_avg_rating = avg_rating(user)


    for a,r in user.items():
        if r is None: # if the user P has not rated artist a...
            rating = 0.0
            for other_user in otherUsers: # loop through each user in otherUsers
                other_user_avg_rating = avg_rating(otherUsers[other_user])
                r2 = otherUsers[other_user][a] # the other user's rating of artist a
                if r2 is not None: # if the other user HAS rated artist a
                    to_add = similarityFunction(user, otherUsers[other_user]) * (r2 - other_user_avg_rating)
                    rating += to_add
                else:
                    continue
            if z != 0.0: # don't want to divide by zero
                weighted_rating = rating / z
            else:
                weighted_rating = 0

            adj_weighted_rating = user_avg_rating + weighted_rating
            tup = (a, adj_weighted_rating)
            ratings_list.append(tup)
        else:
            continue

    # sort rating list
    ratings_list = sorted(ratings_list, key=itemgetter(1), reverse=True)
    return ratings_list

def main():

    #1) take in two parameters as input
    try:
        file_forRecs = sys.argv[1]
        file_otherUsers = sys.argv[2]
    except IndexError:
        print("Two files required for execution")
        exit(0)

    #2) open input files, read in user histories from each
    file_forRecs = open(file_forRecs, "r")
    file_otherUsers = open(file_otherUsers, "r")

    # open favorites file
    lastfm_favorites = open('lastfm_favorites.csv', "r")

    #2a) generate a list of all artists between both lists of users.
    all_artists = []
    favorite_artists = []
    all_artists = getArtists(file_forRecs, all_artists)
    all_artists = getArtists(file_otherUsers, all_artists)

    recUsers = {}
    otherUsers = {}
    recUsersFavorites = {}

    #3) convert history of each user into single instance p per user and append instance to its appropriate list
    file_forRecs.seek(0) # reset file
    file_otherUsers.seek(0) # reset file
    process(file_forRecs, all_artists, recUsers) # recUsers now contains instances from file_forRecs
    process(file_otherUsers, all_artists, otherUsers) #otherUsers now contains instances from file_otherUsers
    process(lastfm_favorites, favorite_artists, recUsersFavorites) # create an accessible dictionary for later when comparing program output to users' actual favorite songs

    # next, identify the n most similar users from otherUsers FOR EACH user in recUsers
    recUsers_similar = {}
    for user in recUsers:
        similarity_list = []  # list to contain the similar users to a single user from recUsers.
        for other_user in otherUsers:
            # call similarity function
            similarity = similarityFunction(recUsers[user], otherUsers[other_user])
            tup = (other_user, similarity)
            similarity_list.append(tup)

        # need to sort similarity list from most similar to least.
        similarity_list.sort(key = lambda tup: tup[1], reverse = True)

        # now truncate list to top 3
        recUsers_similar[user] = similarity_list

    #4) for each user in recUsers, estimate their rating for each artist they have not yet listened to based on data from otherUsers. ++
    #5) CALCULATE ACCURACY OF PREDICTIONS (How well did the recommendation system make recommendations?)
        # we want to calculate how many times each option predicted the user's favorite artist correctly
        # likewise, we also want to calculate how often the user's favorite artist showed up in each user's top 5 recommendations for each of the three options.

    option1_recommendations = {}
    option2_recommendations = {}
    option3_recommendations = {}

    option1_correct, option2_correct, \
    option3_correct, option1_top5correct, \
    option2_top5correct, option3_top5correct = 0, 0, 0, 0, 0, 0


    for user in recUsers_similar.items():
        # option 1 - AVERAGE RATING
        user = (user[0], user[1][:3])
        user_avg_rtg_list = averageRating(user, otherUsers, recUsers)
        user_avg_rtg_list = user_avg_rtg_list[:5] # only want user's top 5
        option1_recommendations[user[0]] = user_avg_rtg_list

        user_favorite = list(recUsersFavorites[user[0]].items())[0][0] # user i's favorite artist from lastfm_favorites.csv

        # top choice predicted correctly? OPTION 1
        if option1_recommendations[user[0]][0][0] == user_favorite:
            option1_correct += 1
        top5_artists = [i[0] for i in option1_recommendations[user[0]]]
        if top5_artists.__contains__(user_favorite):
            option1_top5correct += 1

    for user in recUsers:
        # option 2 - WEIGHTED AVERAGE RATING
        user_wtd_avg_rtg_list = weightedAverageRating(recUsers[user], otherUsers)
        user_wtd_avg_rtg_list = user_wtd_avg_rtg_list[:5] # only want users top 5
        option2_recommendations[user] = user_wtd_avg_rtg_list

        # option 3 - ADJUSTED WEIGHTED AVERAGE RATING
        user_adj_wtd_avg_rtg_list = adjustedWeightedAverageRating(recUsers[user], otherUsers)
        user_adj_wtd_avg_rtg_list = user_adj_wtd_avg_rtg_list[:5] # only want users top 5
        option3_recommendations[user] = user_adj_wtd_avg_rtg_list

        user_favorite = list(recUsersFavorites[user].items())[0][0]  # user i's favorite artist from lastfm_favorites.csv

        # top choice predicted correctly? OPTION 2
        if option2_recommendations[user][0][0] == user_favorite:

            option2_correct += 1
        top5_artists = [i[0] for i in option2_recommendations[user]]
        if top5_artists.__contains__(user_favorite):
            option2_top5correct += 1

        # top choice predicted correctly? OPTION 3
        if option3_recommendations[user][0][0] == user_favorite:
            option3_correct += 1
        top5_artists = [i[0] for i in option3_recommendations[user]]
        if top5_artists.__contains__(user_favorite):
            option3_top5correct += 1

    # program accuracy output
    print()
    print('##### TOP CHOICE PREDICTION ACCURACIES #####')
    print('Option 1, top choice predicted correctly: ', "{:.1%}".format(option1_correct / 50))
    print('Option 2, top choice predicted correctly: ', "{:.1%}".format(option2_correct / 50))
    print('Option 3, top choice predicted correctly: ', "{:.1%}".format(option3_correct / 50))
    print('##### TOP CHOICE PREDICTION ACCURACIES #####')
    print()
    print("##### TOP CHOICE WITHIN USER'S TOP 5 PREDICTION ACCURACIES #####")
    print("Option 1, top choice predicted within user's top 5: ", "{:.1%}".format(option1_top5correct / 50))
    print("Option 2, top choice predicted within user's top 5: ", "{:.1%}".format(option2_top5correct / 50))
    print("Option 3, top choice predicted within user's top 5: ", "{:.1%}".format(option3_top5correct / 50))
    print("##### TOP CHOICE WITHIN USER'S TOP 5 PREDICTION ACCURACIES #####")
    print()


main()