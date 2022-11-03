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

    public static class Reduce extends MapReduceBase implements Reducer<Text, IntWritable, Text, IntWritable> {
        public void reduce(Text key, Iterator<Friendship> values, OutputCollector<Text, Friendship> output) {
            HashMap<String, MutableInt> recommendations = new HashMap<>();
            ArrayList<String> friendsTracker = new ArrayList();
            for (Friendship val : values) {
                String person = val.person.toString();
                if (val.friendship.get() == -1) {
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

            Comparator<Entry<String, MutuableInt>> valueComparator
                = new Comparator<Entry<String, MutuableInt>>() {
                    @Override
                    public int compare(Entry<String, MutuableInt> e1, Entry<String, MutuableInt> e2) {
                        MutableInt v1 = e1.getValue();
                        MutableInt v2 = e2.getValue();
                        int res = v2.compareTo(v1);
                        if (res == 0)
                        {
                            return e2.getValue().compreTo(e1.getValue());
                        }
                    }
                };
                List<Entry<String, MutableInt>> recommendationsList = new ArrayList<Entry<String, MutableInt>>(recommendations.entrySet());
                Collections.sort(recommendationsList, valueComparator);
                StringBuilder recommendationsText = new StringBuilder();

                for (int i = 0; i < 10 && i < recommendationsList.length; i++) {
                    if (friendsTracker.contains(recommendationsList.get(i).getKey())) {
                        continue;
                    }
                    recommendationsText.append(recommendationsList.get(i).getKey()).append(" ");
                }
                output.collect(key, new Text(recommendationsText.toString()));

    }

    public static void main(String[] args) throws IOException, InterruptedException, ClassNotFoundException {
        
    }
}
}