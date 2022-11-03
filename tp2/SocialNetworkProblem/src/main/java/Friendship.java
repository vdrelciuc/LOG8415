package main.java;

import org.apache.hadoop.io.Writable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.io.IntWritable;

import java.io.DataInput;
import java.io.DataOutput;
import java.io.IOException;

public class Friendship implements Writable {
    Text user = new Text();
    IntWritable isFriend = new IntWritable();

    public Friendship(Text friend, IntWritable relation){
        this.user = friend;
        this.isFriend = relation;
    }

    @Override
    public void readFields(DataInput dataInput) throws IOException {
        this.user.readFields(dataInput);
        this.isFriend.readFields(dataInput);
    }

    @Override
    public void write(DataOutput dataOutput) throws IOException {
        this.user.write(dataOutput);
        this.isFriend.write(dataOutput);
    }
}
