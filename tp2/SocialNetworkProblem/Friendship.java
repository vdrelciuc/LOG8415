import org.apache.hadoop.io.IntWritable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.io.Writable;

import java.io.DataInput;
import java.io.DataOutput;
import java.io.IOException;

public class Friendship implements Writable {
    public Text person = new Text();
    public IntWritable isFriend = new IntWritable();

    public Friendship() {}

    public Firendship(Text person, IntWritable relationship) {
        this.person = person;
        this.isFriend = relationship;
    }

    @Override
    public void readFields(DataInput input) {
        this.person.readFields(input);
        this.isFriend.readFields(input);
    }

    @Override
    public void write(DataOutput output) {
        this.person.write(output);
        this.isFriend.write(output);
    }
}