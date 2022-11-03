package com.log8415;

import java.io.IOException;

import org.apache.hadoop.io.IntWritable;
import org.apache.hadoop.io.LongWritable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapred.MapReduceBase;
import org.apache.hadoop.mapred.Mapper;
import org.apache.hadoop.mapred.OutputCollector;
import org.apache.hadoop.mapred.Reporter;

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
}
