package main.java;

import java.io.IOException;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.HashMap;
import java.util.Iterator;
import java.util.List;
import java.util.Map.Entry;

import org.apache.commons.lang.mutable.MutableInt;
import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.io.IntWritable;
import org.apache.hadoop.io.LongWritable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapred.MapReduceBase;
import org.apache.hadoop.mapred.Mapper;
import org.apache.hadoop.mapred.OutputCollector;
import org.apache.hadoop.mapred.Reporter;
import org.apache.hadoop.mapreduce.Job;
import org.apache.hadoop.mapreduce.Reducer;

public class SocialNetworkProblem {
    public static class Map extends MapReduceBase implements Mapper<LongWritable, Text, Text, Friendship> {
        private final static IntWritable one = new IntWritable(1);
        final IntWritable isFriend = new IntWritable(-1);
        final IntWritable isMaybeFriend = new IntWritable(1);

        @Override
        public void map(LongWritable key, Text value, OutputCollector<Text, Friendship> output, Reporter reporter) throws IOException {
            String[] userLine = value.toString().split("\\s");
            Text id = new Text(userLine[0]);
            String[] friends = userLine[1].split(",");

            for (int i = 0; i < friends.length; i++) {
                Text friend = new Text(friends[i]);
                output.collect(friend, new Friendship(friend, isFriend));
                for (int j = i + 1; j < friends.length; j++) {
                    Text maybeFriend = new Text(friends[j]);
                    output.collect(friend, new Friendship(maybeFriend, isMaybeFriend));
                    output.collect(friend, new Friendship(friend, isMaybeFriend));
                }
            }
        }
    }

    public static class Reduce extends Reducer<Text, IntWritable, Text, IntWritable> {
        public void reduce(Text key, Iterator<Friendship> values, OutputCollector<Text, Text> output) throws IOException {
            HashMap<String, MutableInt> recommendations = new HashMap<>();
            ArrayList<String> friendsTracker = new ArrayList<String>();
            while (values.hasNext()) {
                final Friendship val = values.next();
                String person = val.user.toString();
                if (val.isFriend.get() == -1) {
                    friendsTracker.add(person);
                }
                else if (!friendsTracker.contains(person)) {
                    MutableInt mutualFriendsCount = recommendations.get(person);
                    if (mutualFriendsCount == null) {
                        recommendations.put(person, new MutableInt(1));
                    }
                    else {
                        mutualFriendsCount.increment();
                    }
                }
            }

            Comparator<Entry<String, MutableInt>> valueComparator
                = new Comparator<Entry<String, MutableInt>>() {
                    @Override
                    public int compare(Entry<String, MutableInt> e1, Entry<String, MutableInt> e2) {
                        MutableInt v1 = e1.getValue();
                        MutableInt v2 = e2.getValue();
                        int res = v2.compareTo(v1);
                        if (res == 0)
                        {
                            return e2.getValue().compareTo(e1.getValue());
                        }
                        return res;
                    }
                };
                List<Entry<String, MutableInt>> recommendationsList = new ArrayList<Entry<String, MutableInt>>(recommendations.entrySet());
                recommendationsList.sort(valueComparator);
                StringBuilder recommendationsText = new StringBuilder();

                for (int i = 0; i < 10 && i < recommendationsList.size(); i++) {
                    if (friendsTracker.contains(recommendationsList.get(i).getKey())) {
                        continue;
                    }
                    recommendationsText.append(recommendationsList.get(i).getKey()).append(" ");
                }
                output.collect(key, new Text(recommendationsText.toString()));

    }
    }

    public static void main(String[] args) throws IOException {
        Configuration configuration = new Configuration();

        Job job = Job.getInstance(configuration, "social_network_problem");
        job.setJarByClass(SocialNetworkProblem.class);
        job.setMapOutputKeyClass(Map.class);
        job.setOutputValueClass(Friendship.class);
    }
}
