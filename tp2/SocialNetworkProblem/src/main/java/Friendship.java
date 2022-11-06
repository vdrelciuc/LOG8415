package main.java;

import org.apache.hadoop.io.Writable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.io.IntWritable;

import java.io.DataInput;
import java.io.DataOutput;
import java.io.IOException;
/*
 * Friendship class
 * 
 * This class represents the relationship a friend/potential friend has with a user.
 */
public class Friendship implements Writable {
    Text user = new Text();
    IntWritable isFriend = new IntWritable();

    /*
     * Default constructor for the friendship class.
     * Creates a an empty friendship.
     */
    public Friendship() {
    }

    /*
     * Parametric constructor for a friendship relation.
     * 
     * @param   friend      The friend/potential friend to the user
     * @param   relation    The relationship the friend/potential friend has with the user (-1 is a friend, 1 is a potential friend) 
     */
    public Friendship(Text friend, IntWritable relation) {
        this.user = friend;
        this.isFriend = relation;
    }

    /*
     * Method used to read from an input
     * 
     * @param   dataInput   The input containing the data 
     */
    @Override
    public void readFields(DataInput dataInput) throws IOException {
        this.user.readFields(dataInput);
        this.isFriend.readFields(dataInput);
    }

    /*
     * Method used to write on an output
     * 
     * @param dataOutput    The output where to write the data
     */
    @Override
    public void write(DataOutput dataOutput) throws IOException {
        this.user.write(dataOutput);
        this.isFriend.write(dataOutput);
    }

    /*
     * Method to convert Friendship to a string
     * 
     * @return String containing the Friendship information
     */
    @Override
    public String toString() {
        return "Friendship{" +
            "user=" + user +
            ", isFriend=" + (isFriend.get() == 1 ? "maybe" : "yes") +
            '}';
    }
}
