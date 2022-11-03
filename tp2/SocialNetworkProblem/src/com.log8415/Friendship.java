package com.log8415;

import org.apache.hadoop.io.Writable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.io.IntWritable;

import java.io.DataInput;
import java.io.DataOutput;
import java.io.IOException;

public class Friendship implements Writable {
    public Friendship(Text friend, IntWritable relation){

    }

    @Override
    public void readFields(DataInput dataInput) throws IOException {
    }

    @Override
    public void write(DataOutput dataOutput) throws IOException {
    }
}
