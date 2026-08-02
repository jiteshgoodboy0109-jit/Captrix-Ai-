import { initializeApp, getApps, getApp, FirebaseApp } from "firebase/app";
import { getAuth, Auth } from "firebase/auth";
import { getFirestore, doc, setDoc, serverTimestamp, Firestore } from "firebase/firestore";
import { getAnalytics, isSupported } from "firebase/analytics";

export const firebaseConfig = {
  apiKey: process.env.NEXT_PUBLIC_FIREBASE_API_KEY || "AIzaSyBxSNE3VHVr6RfPks9B-9NmTkq_MdKnKdU",
  authDomain: process.env.NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN || "captrix-ai.firebaseapp.com",
  projectId: process.env.NEXT_PUBLIC_FIREBASE_PROJECT_ID || "captrix-ai",
  storageBucket: process.env.NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET || "captrix-ai.firebasestorage.app",
  messagingSenderId: process.env.NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID || "3513448674",
  appId: process.env.NEXT_PUBLIC_FIREBASE_APP_ID || "1:3513448674:web:55b816d76d3b312d7f06bb",
  measurementId: process.env.NEXT_PUBLIC_FIREBASE_MEASUREMENT_ID || "G-C80FLMJF5S"
};

// Initialize Firebase App instance safely for Next.js SSR
let app: FirebaseApp | null = null;
let auth: Auth | null = null;
let db: Firestore | null = null;

if (typeof window !== 'undefined') {
  try {
    app = getApps().length > 0 ? getApp() : initializeApp(firebaseConfig);
    auth = getAuth(app);
    db = getFirestore(app);

    isSupported().then((supported) => {
      if (supported && app) {
        getAnalytics(app);
      }
    });
  } catch (e) {
    console.warn("Firebase client initialization notice:", e);
  }
}

export const syncAnalysisToFirestore = async (analysisData: any, userUid?: string) => {
  try {
    if (typeof window === 'undefined' || !db || !analysisData || !analysisData.upload_id) return;
    const uploadId = String(analysisData.upload_id);
    const docRef = doc(db, "analyses", uploadId);
    
    await setDoc(docRef, {
      upload_id: analysisData.upload_id,
      company_name: analysisData.company_name,
      filename: analysisData.filename,
      health_score: analysisData.ai_report?.health_score || 0,
      executive_summary: analysisData.ai_report?.executive_summary || "",
      user_uid: userUid || auth?.currentUser?.uid || "guest",
      updated_at: serverTimestamp()
    }, { merge: true });
    
    console.log("Analysis dataset synced to Cloud Firestore under upload_id:", uploadId);
  } catch (err) {
    console.warn("Firestore sync optional warning:", err);
  }
};

export { app, auth, db };
