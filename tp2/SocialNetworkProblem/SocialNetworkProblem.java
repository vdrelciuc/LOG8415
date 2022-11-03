import java.io.IOException;
import java.util.*;
import org.apache.hadoop.io.IntWritable;
import org.apache.hadoop.io.LongWritable;
import org.apache.hadoop.io.Text;

public class SocialNetworkProblem {
    public static class Map extends MapReduceBase implements Mapper<LongWritable, Text, Text, IntWritable> {
        private final static IntWritable one = new IntWritable(1);
        final IntWritable isFriend = new IntWritable(-1);
	    final IntWritable isMaybeFriend = new IntWritable(1);
        public void map(LongWritable key, Text value, OutputCollector<Text, Friendship> output) {
            userLine = value.toString().split("\\s");
            id = new Text[userLine[0]];
            friends = userLine[1].split(',');

            for (int i = 0; i < friends.length; i++) {
                friend = new Text(friends[i]);
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