import { NextRequest, NextResponse } from 'next/server';
import clientPromise from '@/lib/mongodb';
import { verifyToken } from '@/lib/auth';

export async function GET(request: NextRequest) {
  try {
    const authHeader = request.headers.get('authorization');
    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      return NextResponse.json(
        { message: 'Unauthorized' },
        { status: 401 }
      );
    }

    const token = authHeader.substring(7);
    const decoded = verifyToken(token);

    if (!decoded) {
      return NextResponse.json(
        { message: 'Invalid token' },
        { status: 401 }
      );
    }

    const client = await clientPromise;
    const db = client.db('ai-doctor-chatbot');
    const usersCollection = db.collection('users');

    const user = await usersCollection.findOne(
      { _id: new (await clientPromise).ObjectId(decoded.userId) },
      { projection: { password: 0 } } // Exclude password
    );

    if (!user) {
      return NextResponse.json(
        { message: 'User not found' },
        { status: 404 }
      );
    }

    const userResponse = {
      id: user._id.toString(),
      email: user.email,
      name: user.name,
      avatar: user.avatar,
      createdAt: user.createdAt,
    };

    return NextResponse.json(userResponse);
  } catch (error) {
    console.error('Get user error:', error);
    return NextResponse.json(
      { message: 'Internal server error' },
      { status: 500 }
    );
  }
}