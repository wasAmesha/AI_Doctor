import { NextRequest, NextResponse } from 'next/server';
import bcrypt from 'bcryptjs';
import clientPromise from '@/lib/mongodb';
import { generateToken } from '@/lib/auth';

export async function POST(request: NextRequest) {
  try {
    const { email, password } = await request.json();

    // Validate input
    if (!email || !password) {
      return NextResponse.json(
        { message: 'Email and password are required' },
        { status: 400 }
      );
    }

    const client = await clientPromise;
    const db = client.db('ai-doctor-chatbot');
    const usersCollection = db.collection('users');

    // Find user
    const user = await usersCollection.findOne({ email });
    if (!user) {
      return NextResponse.json(
        { message: 'Invalid credentials' },
        { status: 401 }
      );
    }

    // Check password
    const isPasswordValid = await bcrypt.compare(password, user.password);
    if (!isPasswordValid) {
      return NextResponse.json(
        { message: 'Invalid credentials' },
        { status: 401 }
      );
    }

    // Generate JWT token
    const token = generateToken({
      userId: user._id.toString(),
      email: user.email,
    });

    // Update last login
    await usersCollection.updateOne(
      { _id: user._id },
      { $set: { updatedAt: new Date() } }
    );

    // Return user data without password
    const userResponse = {
      id: user._id.toString(),
      email: user.email,
      name: user.name,
      avatar: user.avatar,
      createdAt: user.createdAt,
    };

    return NextResponse.json(
      { user: userResponse, token },
      { status: 200 }
    );
  } catch (error) {
    console.error('Login error:', error);
    return NextResponse.json(
      { message: 'Internal server error' },
      { status: 500 }
    );
  }
}