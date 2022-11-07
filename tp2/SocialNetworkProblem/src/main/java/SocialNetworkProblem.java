package main.java;

import java.io.IOException;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.HashMap;
import java.util.Iterator;
import java.util.List;
import java.util.Map.Entry;

import org.apache.commons.lang.mutable.MutableInt;
import org.apache.hadoop.fs.Path;
import org.apache.hadoop.io.IntWritable;
import org.apache.hadoop.io.LongWritable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapred.FileInputFormat;
import org.apache.hadoop.mapred.FileOutputFormat;
import org.apache.hadoop.mapred.JobClient;
import org.apache.hadoop.mapred.JobConf;
import org.apache.hadoop.mapred.MapReduceBase;
import org.apache.hadoop.mapred.Mapper;
import org.apache.hadoop.mapred.OutputCollector;
import org.apache.hadoop.mapred.Reducer;
import org.apache.hadoop.mapred.Reporter;
import org.apache.hadoop.mapred.TextInputFormat;
import org.apache.hadoop.mapred.TextOutputFormat;

public class SocialNetworkProblem {
    /*
     * Map class
     * 
     * This class is used to map the users and theirs friends and ouputs it.
     * 
     * Inherits from the MapReduceBase as it is a Mapreduce functionality.
     * 
     * Implements the Mapper interface.
     */
    public static class Map extends MapReduceBase implements Mapper<LongWritable, Text, Text, Friendship> {
        final IntWritable isFriend = new IntWritable(-1);
        final IntWritable isMaybeFriend = new IntWritable(1);

        @Override
        public void map(LongWritable key, Text value, OutputCollector<Text, Friendship> output, Reporter reporter) throws IOException {
            // We collect the data from the dataset
            String[] userLine = value.toString().split("\\s");

            Text id = new Text(userLine[0]);
            if (userLine.length < 2) { // The user has no friends.
                output.collect(id, new Friendship());
                return;
            }
            String[] friends = userLine[1].split(",");

            for (int i = 0; i < friends.length; i++) {
                //We create the friendship between the user and the current friend
                Text friend = new Text(friends[i]);
                output.collect(id, new Friendship(friend, isFriend));

                //We iterate over the rest of the user's friends and create a potential friendship between the current friend
                //and the others 
                for (int j = i + 1; j < friends.length; j++) {
                    Text maybeFriend = new Text(friends[j]);
                    output.collect(friend, new Friendship(maybeFriend, isMaybeFriend));
                    output.collect(maybeFriend, new Friendship(friend, isMaybeFriend));
                }
            }
        }
    }

    /*
     * Reduce class
     * 
     * This class divides the map in order to solve the Social Network Problem and find the different friend recommandations
     * for the users.
     * 
     * Inherits from the MapReduceBase as it is a Mapreduce functionality.
     * 
     * Implements the Reducer Interface 
     */

    public static class Reduce extends MapReduceBase implements Reducer<Text, Friendship, Text, Text> {
        public void reduce(Text key, Iterator<Friendship> values, OutputCollector<Text, Text> output, Reporter reporter) throws IOException {
            HashMap<String, MutableInt> recommendations = new HashMap<>(); //Contains mutual friends
            ArrayList<String> friendsTracker = new ArrayList<String>(); //Contains all the friendship relations with the user

            //We iterate through each relation (friendship or potential friendship)
            while (values.hasNext()) {
                final Friendship val = values.next();
                String person = val.user.toString();

                if (val.isFriend.get() == -1) { //If they are friends
                    friendsTracker.add(person);
                }
                else if (!friendsTracker.contains(person)) {  
                    MutableInt mutualFriendsCount = recommendations.get(person);
                    if (mutualFriendsCount == null) {
                        //If not not found in the recommendations, we add that person.
                        recommendations.put(person, new MutableInt(1));
                    }
                    else {
                        mutualFriendsCount.increment();
                    }
                }
            }

            //This comaparator will sort the recommandations list from the most mutual friends to the least.
            Comparator<Entry<String, MutableInt>> valueComparator
                = new Comparator<Entry<String, MutableInt>>() {
                @Override
                public int compare(Entry<String, MutableInt> e1, Entry<String, MutableInt> e2) {
                    MutableInt v1 = e1.getValue();
                    MutableInt v2 = e2.getValue();
                    int res = v2.compareTo(v1);
                    if (res == 0) {
                        return e2.getValue().compareTo(e1.getValue());
                    }
                    return res;
                }
            };

            //We sort the recommendations according to the comaprator
            List<Entry<String, MutableInt>> recommendationsList = new ArrayList<Entry<String, MutableInt>>(recommendations.entrySet());
            recommendationsList.sort(valueComparator);
            ArrayList<String> recommendationsTextArr = new ArrayList<>();

            //We select the 10 users with the most mutual friends
            for (int i = 0; i < 10 && i < recommendationsList.size(); i++) {
                if (friendsTracker.contains(recommendationsList.get(i).getKey())) {
                    continue;
                }
                recommendationsTextArr.add(recommendationsList.get(i).getKey());
            }

            output.collect(key, new Text(String.join(",", recommendationsTextArr)));

        }
    }

    /**
        Main method of our app.
        Expects first argument to be the path of the input dataset
        Expects second argument to be the path of the output result
     */
    public static void main(String[] args) throws IOException {
        JobConf conf = new JobConf(SocialNetworkProblem.class);
        conf.setJobName("social-network-problem");

        conf.setOutputKeyClass(Text.class);
        conf.setOutputValueClass(Friendship.class);

        conf.setMapperClass(Map.class);
        conf.setReducerClass(Reduce.class);

        conf.setInputFormat(TextInputFormat.class);
        conf.setOutputFormat(TextOutputFormat.class);

        FileInputFormat.setInputPaths(conf, new Path(args[0]));
        FileOutputFormat.setOutputPath(conf, new Path(args[1]));

        JobClient.runJob(conf);
    }
}
