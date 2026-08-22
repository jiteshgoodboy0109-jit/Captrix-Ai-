import React, { useState, useRef, useEffect, Suspense } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { OrbitControls, PerspectiveCamera, Environment, ContactShadows, Float } from '@react-three/drei';
import * as THREE from 'three';
import { 
  Sparkles, 
  Eye, 
  Package, 
  Sun, 
  RotateCcw, 
  Check, 
  ShoppingBag, 
  ChevronRight, 
  Star, 
  ShieldCheck, 
  Truck, 
  Award,
  Phone,
  Mail,
  MapPin,
  Maximize2,
  Minimize2,
  Lightbulb,
  Heart,
  Share2
} from 'lucide-react';

// ==========================================
// 3D Lantern Mooncake Box Canvas & Model
// ==========================================

function Mooncake({ position, rotation, scale = [1, 1, 1], patternColor = "#D4AF37", label = "" }) {
  const meshRef = useRef();

  useFrame((state, delta) => {
    if (meshRef.current) {
      meshRef.current.rotation.y += delta * 0.2;
    }
  });

  return (
    <group position={position} rotation={rotation} scale={scale}>
      {/* Main Mooncake Body - Golden baked crust look */}
      <mesh castShadow receiveShadow>
        <cylinderGeometry args={[0.55, 0.58, 0.38, 32]} />
        <meshStandardMaterial 
          color="#c68a4c"
          roughness={0.4}
          metalness={0.15}
          bumpScale={0.05}
        />
      </mesh>

      {/* Top Crimped Edge Detail */}
      <mesh position={[0, 0.19, 0]}>
        <cylinderGeometry args={[0.56, 0.55, 0.04, 24]} />
        <meshStandardMaterial color="#b3783a" roughness={0.3} />
      </mesh>

      {/* Embossed Top Pattern Ring */}
      <mesh position={[0, 0.205, 0]} rotation={[-Math.PI / 2, 0, 0]}>
        <ringGeometry args={[0.25, 0.5, 32]} />
        <meshStandardMaterial color="#d49a55" roughness={0.3} metalness={0.2} />
      </mesh>

      {/* Center Seal Emblem */}
      <mesh position={[0, 0.21, 0]} rotation={[-Math.PI / 2, 0, 0]}>
        <circleGeometry args={[0.24, 32]} />
        <meshStandardMaterial color="#8B0000" roughness={0.3} />
      </mesh>

      {/* Golden Character / Motif */}
      <mesh position={[0, 0.215, 0]} rotation={[-Math.PI / 2, 0, 0]}>
        <ringGeometry args={[0.08, 0.18, 4]} />
        <meshStandardMaterial color="#F59E0B" roughness={0.2} metalness={0.8} />
      </mesh>
    </group>
  );
}

function LanternBox3D({ isOpen, isLightOn, activeFlavor }) {
  const boxRef = useRef();
  const topCoverRef = useRef();
  const leftDoorRef = useRef();
  const rightDoorRef = useRef();

  // Animation values using useFrame for smooth lerping
  useFrame((state, delta) => {
    const targetDoorAngle = isOpen ? Math.PI * 0.45 : 0;
    const targetTopOffset = isOpen ? 0.3 : 0;

    if (leftDoorRef.current) {
      leftDoorRef.current.rotation.y = THREE.MathUtils.lerp(
        leftDoorRef.current.rotation.y,
        -targetDoorAngle,
        delta * 3
      );
    }
    if (rightDoorRef.current) {
      rightDoorRef.current.rotation.y = THREE.MathUtils.lerp(
        rightDoorRef.current.rotation.y,
        targetDoorAngle,
        delta * 3
      );
    }
    if (topCoverRef.current) {
      topCoverRef.current.position.y = THREE.MathUtils.lerp(
        topCoverRef.current.position.y,
        1.3 + targetTopOffset,
        delta * 3
      );
    }
  });

  return (
    <group ref={boxRef} position={[0, -0.4, 0]}>
      {/* Lantern Inner Glow Light */}
      <pointLight 
        position={[0, 0.6, 0]} 
        intensity={isLightOn ? 8 : 0.2} 
        color="#FDE047" 
        distance={4}
        decay={2}
      />
      <pointLight 
        position={[0, 0.2, 0]} 
        intensity={isLightOn ? 5 : 0.1} 
        color="#F97316" 
        distance={3}
      />

      {/* Base Pedestal / Tray */}
      <mesh position={[0, -0.05, 0]} receiveShadow castShadow>
        <cylinderGeometry args={[1.25, 1.35, 0.12, 8]} />
        <meshStandardMaterial color="#4A0E17" roughness={0.3} metalness={0.6} />
      </mesh>

      {/* Metallic Gold Base Rim */}
      <mesh position={[0, 0.02, 0]}>
        <cylinderGeometry args={[1.26, 1.26, 0.03, 8]} />
        <meshStandardMaterial color="#D4AF37" metalness={0.9} roughness={0.2} />
      </mesh>

      {/* Inner Central Column / Lamp Shade Structure */}
      <mesh position={[0, 0.6, 0]}>
        <cylinderGeometry args={[0.55, 0.55, 1.1, 16, 1, true]} />
        <meshStandardMaterial 
          color={isLightOn ? "#FFFBEB" : "#FEF3C7"} 
          emissive={isLightOn ? "#FDE047" : "#000000"} 
          emissiveIntensity={isLightOn ? 0.8 : 0}
          transparent={true}
          opacity={0.85}
          side={THREE.DoubleSide}
        />
      </mesh>

      {/* Inner Golden Paper Cutout Lattice Frame */}
      <mesh position={[0, 0.6, 0]}>
        <cylinderGeometry args={[0.56, 0.56, 1.12, 8, 1, true]} />
        <meshStandardMaterial 
          color="#B91C1C" 
          wireframe={true}
          wireframeLinewidth={3}
        />
      </mesh>

      {/* 4 Mooncakes placed around the inner tray when opened */}
      <group position={[0, 0.15, 0]}>
        <Mooncake position={[0.65, 0.15, 0]} rotation={[0, 0, 0]} patternColor="#EAB308" />
        <Mooncake position={[-0.65, 0.15, 0]} rotation={[0, Math.PI / 2, 0]} patternColor="#EF4444" />
        <Mooncake position={[0, 0.15, 0.65]} rotation={[0, Math.PI, 0]} patternColor="#10B981" />
        <Mooncake position={[0, 0.15, -0.65]} rotation={[0, -Math.PI / 2, 0]} patternColor="#8B5CF6" />
      </group>

      {/* Outer Shell Left Door */}
      <group position={[-0.6, 0.6, 0]} ref={leftDoorRef}>
        <mesh position={[0.3, 0, 0]} castShadow receiveShadow>
          <boxGeometry args={[0.6, 1.15, 1.1]} />
          <meshStandardMaterial color="#800913" roughness={0.3} metalness={0.4} />
        </mesh>
        {/* Gold Border Trimming */}
        <mesh position={[0.6, 0, 0]}>
          <boxGeometry args={[0.02, 1.16, 1.11]} />
          <meshStandardMaterial color="#F59E0B" metalness={0.9} roughness={0.1} />
        </mesh>
      </group>

      {/* Outer Shell Right Door */}
      <group position={[0.6, 0.6, 0]} ref={rightDoorRef}>
        <mesh position={[-0.3, 0, 0]} castShadow receiveShadow>
          <boxGeometry args={[0.6, 1.15, 1.1]} />
          <meshStandardMaterial color="#800913" roughness={0.3} metalness={0.4} />
        </mesh>
        {/* Gold Border Trimming */}
        <mesh position={[-0.6, 0, 0]}>
          <boxGeometry args={[0.02, 1.16, 1.11]} />
          <meshStandardMaterial color="#F59E0B" metalness={0.9} roughness={0.1} />
        </mesh>
      </group>

      {/* Top Pagoda Cap & Handle Assembly */}
      <group position={[0, 1.3, 0]} ref={topCoverRef}>
        {/* Roof Pyramid */}
        <mesh position={[0, 0, 0]} castShadow>
          <coneGeometry args={[1.35, 0.4, 8]} />
          <meshStandardMaterial color="#580810" roughness={0.3} metalness={0.5} />
        </mesh>
        {/* Roof Gold Rim */}
        <mesh position={[0, -0.18, 0]}>
          <cylinderGeometry args={[1.37, 1.37, 0.04, 8]} />
          <meshStandardMaterial color="#D4AF37" metalness={0.9} roughness={0.2} />
        </mesh>
        {/* Carrying Handle Loop */}
        <mesh position={[0, 0.35, 0]} rotation={[0, 0, 0]}>
          <torusGeometry args={[0.22, 0.035, 16, 32, Math.PI]} />
          <meshStandardMaterial color="#F59E0B" metalness={0.9} roughness={0.1} />
        </mesh>
        {/* Tassel Attachment */}
        <mesh position={[0, 0.22, 0]}>
          <cylinderGeometry args={[0.06, 0.06, 0.15, 16]} />
          <meshStandardMaterial color="#D4AF37" metalness={0.9} />
        </mesh>
      </group>
    </group>
  );
}

// ==========================================
// Main Application Component
// ==========================================
export default function App() {
  const [boxOpen, setBoxOpen] = useState(false);
  const [lightOn, setLightOn] = useState(true);
  const [activeFlavor, setActiveFlavor] = useState(0);
  const [orderQuantity, setOrderQuantity] = useState(1);
  const [selectedBoxType, setSelectedBoxType] = useState('full');
  const [orderSubmitted, setOrderSubmitted] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [activeTab, setActiveTab] = useState('all');

  const [formData, setFormData] = useState({
    name: '',
    phone: '',
    email: '',
    address: '',
    notes: '',
    customLogo: false,
  });

  const flavors = [
    {
      id: 1,
      name: "Thập Cẩm Bát Bửu Hoàng Gia",
      subtitle: "Xốt Bào Ngư & Vây Cá Hại Vị",
      category: "savory",
      price: "320.000đ / cái",
      desc: "Sự kết hợp tinh túy giữa vi cá, bào ngư thượng hạng cùng 8 vị hạt ngũ cô truyền thống. Vị mặn ngọt hài hòa mang nét thanh nhã hoàng cung.",
      tags: ["Vi cá", "Bào ngư", "Hạt dưa", "Mứt quất"],
      image: "https://images.unsplash.com/photo-1631787424227-bbd3bcbeceec?auto=format&fit=crop&q=80&w=800",
      color: "from-amber-600 to-amber-900",
    },
    {
      id: 2,
      name: "Trà Xanh Tôm Nướng Trứng Muối",
      subtitle: "Hương Trà Ô Long Matcha Nhật Bản",
      category: "sweet",
      price: "280.000đ / cái",
      desc: "Lớp vỏ xanh ngọc mướt mát từ bột trà xanh Kyoto, ôm trọn nhân lòng đỏ trứng muối béo ngậy thanh dịu đượm vị trà thanh khiết.",
      tags: ["Trà xanh Matcha", "Trứng muối", "Hạt sen"],
      image: "https://images.unsplash.com/photo-1509440159596-0249088772ff?auto=format&fit=crop&q=80&w=800",
      color: "from-emerald-700 to-teal-950",
    },
    {
      id: 3,
      name: "Thượng Hạng Yến Sào Hải Sản",
      subtitle: "Sâm Khánh Hòa & Hải Sản Biển Đông",
      category: "premium",
      price: "350.000đ / cái",
      desc: "Chiết xuất yến sào tự nhiên hòa quyện với hải sản tươi ngon. Món quà sức khỏe đẳng cấp thể hiện sự tri ân chân thành.",
      tags: ["Yến sào", "Hải sản", "Đông trùng hạ thảo"],
      image: "https://images.unsplash.com/photo-1541781774459-bb2af2f05b55?auto=format&fit=crop&q=80&w=800",
      color: "from-amber-500 to-red-900",
    },
    {
      id: 4,
      name: "Hạt Sen Táo Đỏ Kỷ Tử",
      subtitle: "Thanh Vị Dưỡng Tâm Thuần Túy",
      category: "sweet",
      price: "250.000đ / cái",
      desc: "Nhân hạt sen Huế dẻo mịn kết hợp cùng vị ngọt tự nhiên của táo đỏ và kỷ tử. Phù hợp cho những buổi trà chiều thưởng nguyệt.",
      tags: ["Hạt sen Huế", "Táo đỏ", "Kỷ tử", "Ít đường"],
      image: "https://images.unsplash.com/photo-1563729784474-d77dbb933a9e?auto=format&fit=crop&q=80&w=800",
      color: "from-yellow-700 to-amber-950",
    },
    {
      id: 5,
      name: "Lava Sô-cô-la Trứng Chảy",
      subtitle: "Sốt Kem Trứng Nóng Chảy Tan Chảy",
      category: "modern",
      price: "290.000đ / cái",
      desc: "Sự bứt phá hiện đại với dòng sốt trứng muối tan chảy béo ngậy tuôn trào khi cắt bánh. Vỏ bánh nướng thơm lừng chuẩn vị.",
      tags: ["Lava trứng chảy", "Sô-cô-la 70%", "Bơ Pháp"],
      image: "https://images.unsplash.com/photo-1606313564200-e75d5e30476c?auto=format&fit=crop&q=80&w=800",
      color: "from-orange-600 to-red-950",
    },
    {
      id: 6,
      name: "Đậu Xanh Mạt Chà Mè Đen",
      subtitle: "Bí Truyền Thanh Đạm Truyền Thống",
      category: "sweet",
      price: "240.000đ / cái",
      desc: "Hương thơm dịu bùi của mè đen rang thủ công quyện cùng đậu xanh mịn màng. Lưu giữ hương vị mộc mạc của Tết Trung Thu xưa.",
      tags: ["Đậu xanh", "Mè đen", "Hạt dưa"],
      image: "https://images.unsplash.com/photo-1587314168485-3236d6710814?auto=format&fit=crop&q=80&w=800",
      color: "from-stone-700 to-stone-900",
    }
  ];

  const filteredFlavors = activeTab === 'all' 
    ? flavors 
    : flavors.filter(f => f.category === activeTab);

  const unitPrice = selectedBoxType === 'full' ? 1280000 : 880000;
  const totalPrice = unitPrice * orderQuantity;
  const discount = orderQuantity >= 5 ? totalPrice * 0.1 : 0;
  const finalPrice = totalPrice - discount;

  const handleFormSubmit = (e) => {
    e.preventDefault();
    setIsSubmitting(true);
    setTimeout(() => {
      setIsSubmitting(false);
      setOrderSubmitted(true);
    }, 1200);
  };

  return (
    <div className="min-h-screen bg-[#0F070A] text-amber-50 selection:bg-amber-500 selection:text-black font-sans antialiased">

      {/* ================= HEADER / NAVBAR ================= */}
      <header className="sticky top-0 z-50 backdrop-blur-md bg-[#0F070A]/85 border-b border-amber-900/30">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-20 flex items-center justify-between">
          
          {/* Brand Logo */}
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-full bg-gradient-to-tr from-amber-600 via-amber-400 to-amber-200 p-[1px] shadow-[0_0_15px_rgba(245,158,11,0.3)]">
              <div className="w-full h-full bg-[#1A0B0E] rounded-full flex items-center justify-center">
                <Sparkles className="w-5 h-5 text-amber-400 animate-pulse" />
              </div>
            </div>
            <div>
              <span className="text-xl font-bold tracking-widest text-transparent bg-clip-text bg-gradient-to-r from-amber-200 via-amber-400 to-amber-100 uppercase font-serif">
                TỎA
              </span>
              <span className="block text-[10px] tracking-[0.25em] text-amber-400/80 uppercase">
                Mooncake Collection
              </span>
            </div>
          </div>

          {/* Navigation Links */}
          <nav className="hidden md:flex items-center space-x-8 text-sm font-medium">
            <a href="#hero" className="text-amber-200/80 hover:text-amber-300 transition-colors">Trang Chủ</a>
            <a href="#3d-experience" className="text-amber-200/80 hover:text-amber-300 transition-colors flex items-center gap-1.5">
              <Eye className="w-4 h-4 text-amber-400" /> Trải Nghiệm 3D
            </a>
            <a href="#cauchuyen" className="text-amber-200/80 hover:text-amber-300 transition-colors">Câu Chuyện</a>
            <a href="#huongvi" className="text-amber-200/80 hover:text-amber-300 transition-colors">Hương Vị</a>
            <a href="#dathang" className="text-amber-200/80 hover:text-amber-300 transition-colors">Đặt Hàng</a>
          </nav>

          {/* CTA Button */}
          <div className="flex items-center gap-4">
            <a 
              href="#dathang" 
              className="px-5 py-2.5 rounded-full text-xs font-semibold uppercase tracking-wider text-stone-950 bg-gradient-to-r from-amber-300 via-amber-400 to-amber-500 hover:brightness-110 shadow-[0_0_20px_rgba(245,158,11,0.4)] transition-all duration-300 transform hover:-translate-y-0.5 active:translate-y-0"
            >
              Đặt Bánh Ngay
            </a>
          </div>
        </div>
      </header>

      {/* ================= HERO SECTION ================= */}
      <section id="hero" className="relative min-h-[90vh] flex items-center justify-center overflow-hidden py-12">
        {/* Background Glowing Orbs */}
        <div className="absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-amber-600/10 rounded-full blur-[140px] pointer-events-none" />
        <div className="absolute bottom-10 right-10 w-96 h-96 bg-red-900/20 rounded-full blur-[100px] pointer-events-none" />

        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10 w-full grid grid-cols-1 lg:grid-cols-12 gap-12 items-center">
          
          {/* Left Text Column */}
          <div className="lg:col-span-6 space-y-6 text-center lg:text-left">
            <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-amber-500/10 border border-amber-500/30 text-amber-300 text-xs font-medium uppercase tracking-widest backdrop-blur-md">
              <Sun className="w-3.5 h-3.5 text-amber-400" />
              Bộ Sưu Tập Trung Thu 2024
            </div>

            <h1 className="text-4xl sm:text-6xl lg:text-7xl font-bold tracking-tight font-serif text-white leading-tight">
              TỎA
              <span className="block text-2xl sm:text-4xl lg:text-5xl font-sans font-light italic text-transparent bg-clip-text bg-gradient-to-r from-amber-200 via-amber-400 to-yellow-500 mt-2">
                Ánh Trăng Thu Khởi Sắc Hoàng Kim
              </span>
            </h1>

            <p className="text-base sm:text-lg text-amber-100/70 max-w-2xl font-light leading-relaxed">
              Tuyệt tác hộp bánh trung thu thiết kế theo hình dáng **Chiếc Đèn Lồng Hoàng Gia**. Hộp bánh tích hợp hệ thống đèn LED ấm áp, hóa thân thành chiếc đèn trang trí tinh tế cho không gian đêm Rằm đoàn viên.
            </p>

            <div className="pt-4 flex flex-col sm:flex-row items-center justify-center lg:justify-start gap-4">
              <a 
                href="#3d-experience" 
                className="w-full sm:w-auto px-8 py-4 rounded-full bg-gradient-to-r from-amber-400 via-yellow-500 to-amber-600 text-stone-950 font-semibold text-sm tracking-wide shadow-lg shadow-amber-500/20 hover:shadow-amber-500/40 hover:scale-105 transition-all duration-300 flex items-center justify-center gap-2"
              >
                <Eye className="w-4 h-4" /> Khám Phá Hộp 3D
              </a>
              <a 
                href="#huongvi" 
                className="w-full sm:w-auto px-8 py-4 rounded-full border border-amber-500/30 text-amber-200 hover:bg-amber-500/10 font-semibold text-sm tracking-wide transition-all duration-300 flex items-center justify-center gap-2"
              >
                Xem 6 Vị Bánh Thượng Hạng
              </a>
            </div>

            {/* Feature Badges */}
            <div className="pt-8 border-t border-amber-900/30 grid grid-cols-3 gap-4 text-center">
              <div>
                <span className="block text-2xl font-bold text-amber-400 font-serif">100%</span>
                <span className="text-xs text-amber-200/60">Thủ Công Nghệ Nhân</span>
              </div>
              <div>
                <span className="block text-2xl font-bold text-amber-400 font-serif">LED 360°</span>
                <span className="text-xs text-amber-200/60">Đèn Lồng Thắp Sáng</span>
              </div>
              <div>
                <span className="block text-2xl font-bold text-amber-400 font-serif">6 Vị</span>
                <span className="text-xs text-amber-200/60">Cao Cấp Độc Bản</span>
              </div>
            </div>
          </div>

          {/* Right Visual Image */}
          <div className="lg:col-span-6 relative flex justify-center">
            <div className="relative w-full max-w-lg aspect-square rounded-3xl overflow-hidden border border-amber-500/20 shadow-[0_0_50px_rgba(245,158,11,0.15)] group">
              <img 
                src="https://images.unsplash.com/photo-1631787424227-bbd3bcbeceec?auto=format&fit=crop&q=80&w=1200" 
                alt="Bộ sưu tập bánh trung thu Tỏa" 
                className="w-full h-full object-cover transform group-hover:scale-105 transition-transform duration-700"
              />
              <div className="absolute inset-0 bg-gradient-to-t from-[#0F070A] via-transparent to-transparent opacity-80" />
              
              <div className="absolute bottom-6 left-6 right-6 p-4 rounded-2xl bg-[#1A0B0E]/80 backdrop-blur-md border border-amber-500/30 flex items-center justify-between">
                <div>
                  <h4 className="text-sm font-semibold text-amber-300">Hộp Quà Đèn Lồng "TỎA"</h4>
                  <p className="text-xs text-amber-100/60">Kèm 4 bánh thượng hạng & Bộ trà cao cấp</p>
                </div>
                <span className="text-lg font-bold text-amber-400 font-serif">1.280.000đ</span>
              </div>
            </div>
          </div>

        </div>
      </section>

      {/* ================= 3D INTERACTIVE EXPERIENCE ================= */}
      <section id="3d-experience" className="py-20 bg-gradient-to-b from-[#0F070A] via-[#160B0E] to-[#0F070A] border-y border-amber-900/30">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          
          <div className="text-center max-w-3xl mx-auto space-y-4 mb-10">
            <span className="text-xs uppercase tracking-[0.3em] text-amber-400 font-semibold">
              Trải Nghiệm Tương Tác Trực Quan
            </span>
            <h2 className="text-3xl sm:text-5xl font-bold font-serif text-white">
              Mở Hộp Bánh & Cảm Nhận Ánh Trăng
            </h2>
            <p className="text-sm sm:text-base text-amber-100/70">
              Xoay 360 độ, bật/tắt ánh đèn lồng rực rỡ và mở cánh cửa hộp để khám phá những chiếc bánh nướng dát kim tuyệt mỹ bên trong.
            </p>
          </div>

          <div className="relative bg-[#180A0E] border border-amber-500/30 rounded-3xl overflow-hidden shadow-2xl min-h-[500px] lg:min-h-[620px] flex flex-col">
            
            {/* 3D Canvas Stage */}
            <div className="w-full flex-1 relative cursor-grab active:cursor-grabbing">
              <Canvas shadows camera={{ position: [0, 1.2, 3.8], fov: 45 }}>
                <ambientLight intensity={0.5} />
                <directionalLight position={[5, 8, 5]} intensity={1.2} castShadow />
                <directionalLight position={[-5, 3, -5]} intensity={0.4} color="#FDE047" />
                
                <Suspense fallback={null}>
                  <Float speed={1.5} rotationIntensity={0.2} floatIntensity={0.2}>
                    <LanternBox3D isOpen={boxOpen} isLightOn={lightOn} activeFlavor={activeFlavor} />
                  </Float>
                  <Environment preset="city" />
                  <ContactShadows position={[0, -0.6, 0]} opacity={0.6} scale={10} blur={2} far={4} />
                </Suspense>

                <OrbitControls 
                  enableZoom={true} 
                  maxPolarAngle={Math.PI / 2 + 0.1} 
                  minDistance={2.2} 
                  maxDistance={6}
                />
              </Canvas>

              {/* Overlay Guidance Badge */}
              <div className="absolute top-4 left-4 bg-black/40 backdrop-blur-md border border-amber-500/20 px-3 py-1.5 rounded-full text-xs text-amber-300/80 flex items-center gap-2 pointer-events-none">
                <RotateCcw className="w-3.5 h-3.5" /> Kéo chuột để xoay 360° • Lăn chuột để Zoom
              </div>
            </div>

            {/* Interactive Control Dock Bar */}
            <div className="p-4 sm:p-6 bg-[#0E0608]/90 backdrop-blur-md border-t border-amber-900/40 flex flex-wrap items-center justify-between gap-4">
              
              {/* Left Action Switches */}
              <div className="flex items-center gap-3">
                <button
                  onClick={() => setBoxOpen(!boxOpen)}
                  className={`px-5 py-2.5 rounded-xl font-semibold text-xs uppercase tracking-wider transition-all duration-300 flex items-center gap-2 border ${
                    boxOpen 
                      ? 'bg-amber-500 text-stone-950 border-amber-400 shadow-[0_0_15px_rgba(245,158,11,0.4)]' 
                      : 'bg-amber-950/40 text-amber-200 border-amber-500/30 hover:bg-amber-900/50'
                  }`}
                >
                  <Package className="w-4 h-4" />
                  {boxOpen ? "Đóng Hộp Bánh" : "Khai Mở Hộp Bánh"}
                </button>

                <button
                  onClick={() => setLightOn(!lightOn)}
                  className={`px-5 py-2.5 rounded-xl font-semibold text-xs uppercase tracking-wider transition-all duration-300 flex items-center gap-2 border ${
                    lightOn 
                      ? 'bg-yellow-400 text-stone-950 border-yellow-300 shadow-[0_0_20px_rgba(250,204,21,0.5)]' 
                      : 'bg-stone-900 text-amber-200/50 border-stone-800 hover:text-amber-200'
                  }`}
                >
                  <Lightbulb className="w-4 h-4" />
                  {lightOn ? "Tắt Đèn Lồng" : "Bật Đèn Lồng (Phát Sáng)"}
                </button>
              </div>

              {/* Status Indicator */}
              <div className="text-xs text-amber-200/60 flex items-center gap-2">
                <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping" />
                <span>Trạng thái: <strong className="text-amber-300">{boxOpen ? "Đã Khai Mở" : "Đóng Gói Hoàng Gia"}</strong></span>
              </div>
            </div>

          </div>

        </div>
      </section>

      {/* ================= HOW IT'S MADE / UNBOXING STEPS ================= */}
      <section className="py-20 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center max-w-3xl mx-auto space-y-4 mb-16">
          <span className="text-xs uppercase tracking-[0.3em] text-amber-400 font-semibold">
            HÀNH TRÌNH TỌA BÁN RÓN
          </span>
          <h2 className="text-3xl sm:text-4xl font-bold font-serif text-white">
            Quy Trình Khai Mở Bánh Trung Thu Vỏ Đèn Lồng
          </h2>
          <p className="text-amber-100/70 text-sm">
            Mỗi chi tiết nhỏ trên vỏ hộp đều được thiết kế tỉ mỉ mang trọn tâm huyết của người nghệ nhân thủ công.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          
          {/* Step 1 */}
          <div className="bg-[#180A0E] border border-amber-900/40 rounded-2xl p-6 relative group hover:border-amber-500/50 transition-all duration-300">
            <div className="aspect-video mb-6 rounded-xl overflow-hidden border border-amber-500/20">
              <img 
                src="https://images.unsplash.com/photo-1541781774459-bb2af2f05b55?auto=format&fit=crop&q=80&w=600" 
                alt="Chạm mở quai xách" 
                className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
              />
            </div>
            <span className="text-3xl font-serif font-bold text-amber-400/30 absolute top-4 right-6">01</span>
            <h3 className="text-lg font-bold text-amber-200 mb-2 font-serif">01. CHẠM SỚM MẮT LỒNG</h3>
            <p className="text-xs text-amber-100/70 leading-relaxed">
              Kéo nhẹ quai xách metallic mạ vàng cao cấp. Lớp chốt nam thềm từ tính êm ái mở ra phong vị sang trọng.
            </p>
          </div>

          {/* Step 2 */}
          <div className="bg-[#180A0E] border border-amber-900/40 rounded-2xl p-6 relative group hover:border-amber-500/50 transition-all duration-300">
            <div className="aspect-video mb-6 rounded-xl overflow-hidden border border-amber-500/20">
              <img 
                src="https://images.unsplash.com/photo-1509440159596-0249088772ff?auto=format&fit=crop&q=80&w=600" 
                alt="Thắp sáng đèn lồng" 
                className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
              />
            </div>
            <span className="text-3xl font-serif font-bold text-amber-400/30 absolute top-4 right-6">02</span>
            <h3 className="text-lg font-bold text-amber-200 mb-2 font-serif">02. THƯỞNG HOA SOI BÓNG</h3>
            <p className="text-xs text-amber-100/70 leading-relaxed">
              Nâng nhẹ tầng đèn lồng. Ánh sáng vàng dịu từ lõi LED chiếu qua khe hoa văn cắt laser sắc nét, lung linh huyền ảo.
            </p>
          </div>

          {/* Step 3 */}
          <div className="bg-[#180A0E] border border-amber-900/40 rounded-2xl p-6 relative group hover:border-amber-500/50 transition-all duration-300">
            <div className="aspect-video mb-6 rounded-xl overflow-hidden border border-amber-500/20">
              <img 
                src="https://images.unsplash.com/photo-1563729784474-d77dbb933a9e?auto=format&fit=crop&q=80&w=600" 
                alt="Thưởng thức bánh" 
                className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
              />
            </div>
            <span className="text-3xl font-serif font-bold text-amber-400/30 absolute top-4 right-6">03</span>
            <h3 className="text-lg font-bold text-amber-200 mb-2 font-serif">03. THƯỞNG VỊ TRUNG THU</h3>
            <p className="text-xs text-amber-100/70 leading-relaxed">
              Mở trọn lòng hộp để chiêm ngưỡng 4 chiếc bánh nướng dát hoa văn dẻo thơm, sẵn sàng thắp lên ấm áp đêm Trăng.
            </p>
          </div>

        </div>
      </section>

      {/* ================= FLAVOR CATALOGUE ================= */}
      <section id="huongvi" className="py-20 bg-[#14080B] border-t border-amber-900/30">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          
          <div className="text-center max-w-3xl mx-auto space-y-4 mb-12">
            <span className="text-xs uppercase tracking-[0.3em] text-amber-400 font-semibold">
              BẢNG HƯƠNG VỊ THƯỢNG HẠNG
            </span>
            <h2 className="text-3xl sm:text-5xl font-bold font-serif text-white">
              6 Hương Vị Bánh Nghệ Nhân Độc Bản
            </h2>
            <p className="text-amber-100/70 text-sm">
              Sự giao thoa hoàn hảo giữa công thức bí truyền hoàng gia và hơi thở ẩm thực hiện đại.
            </p>

            {/* Category Filter Tabs */}
            <div className="flex flex-wrap items-center justify-center gap-2 pt-6">
              {[
                { id: 'all', label: 'Tất Cả Vị' },
                { id: 'savory', label: 'Thập Cẩm Mặn' },
                { id: 'sweet', label: 'Nhân Ngọt Thanh' },
                { id: 'premium', label: 'Hải Sản Cao Cấp' },
                { id: 'modern', label: 'Trứng Chảy Modern' }
              ].map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`px-4 py-2 rounded-full text-xs font-semibold tracking-wider transition-all duration-300 border ${
                    activeTab === tab.id
                      ? 'bg-amber-500 text-stone-950 border-amber-400 shadow-[0_0_12px_rgba(245,158,11,0.3)]'
                      : 'bg-amber-950/20 text-amber-200/70 border-amber-900/40 hover:text-amber-200 hover:border-amber-700'
                  }`}
                >
                  {tab.label}
                </button>
              ))}
            </div>
          </div>

          {/* Flavors Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {filteredFlavors.map((item, idx) => (
              <div 
                key={item.id} 
                className="bg-[#1A0B0E] border border-amber-900/40 rounded-2xl overflow-hidden hover:border-amber-500/60 transition-all duration-300 group flex flex-col justify-between"
              >
                <div>
                  {/* Flavor Image Header */}
                  <div className="relative aspect-[4/3] overflow-hidden">
                    <img 
                      src={item.image} 
                      alt={item.name} 
                      className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-700"
                    />
                    <div className="absolute inset-0 bg-gradient-to-t from-[#1A0B0E] via-transparent to-transparent opacity-90" />
                    
                    <span className="absolute top-4 left-4 px-3 py-1 rounded-full text-[10px] uppercase font-bold tracking-widest bg-black/60 backdrop-blur-md border border-amber-500/30 text-amber-300">
                      Vị #{item.id}
                    </span>

                    <span className="absolute bottom-3 right-4 font-serif text-sm font-bold text-amber-300">
                      {item.price}
                    </span>
                  </div>

                  {/* Flavor Info */}
                  <div className="p-6 space-y-3">
                    <span className="text-[11px] text-amber-400/80 font-medium block">
                      {item.subtitle}
                    </span>
                    <h3 className="text-xl font-bold font-serif text-amber-100 group-hover:text-amber-300 transition-colors">
                      {item.name}
                    </h3>
                    <p className="text-xs text-amber-100/60 leading-relaxed">
                      {item.desc}
                    </p>

                    {/* Ingredient Badges */}
                    <div className="flex flex-wrap gap-1.5 pt-2">
                      {item.tags.map((tag, tIdx) => (
                        <span 
                          key={tIdx} 
                          className="px-2.5 py-1 rounded-md bg-amber-950/60 border border-amber-800/40 text-[10px] text-amber-200/80"
                        >
                          {tag}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>

                <div className="px-6 pb-6 pt-2">
                  <a
                    href="#dathang"
                    onClick={() => setActiveFlavor(idx)}
                    className="w-full py-2.5 rounded-xl border border-amber-500/30 hover:bg-amber-500/10 text-xs font-semibold text-amber-300 flex items-center justify-center gap-2 transition-colors"
                  >
                    Chọn Bánh Vào Hộp <ChevronRight className="w-3.5 h-3.5" />
                  </a>
                </div>
              </div>
            ))}
          </div>

        </div>
      </section>

      {/* ================= ORDER SECTION ================= */}
      <section id="dathang" className="py-20 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        
        <div className="text-center max-w-3xl mx-auto space-y-4 mb-16">
          <span className="text-xs uppercase tracking-[0.3em] text-amber-400 font-semibold">
            ĐẶT HÀNG TRỰC TUYẾN
          </span>
          <h2 className="text-3xl sm:text-5xl font-bold font-serif text-white">
            Sở Hữu Bộ Sưu Tập Trung Thu "TỎA"
          </h2>
          <p className="text-amber-100/70 text-sm">
            Hỗ trợ in logo doanh nghiệp theo yêu cầu, giao hàng tận nơi toàn quốc bảo đảm chất lượng.
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 items-start">
          
          {/* Left Form Column */}
          <div className="lg:col-span-7 bg-[#160A0D] border border-amber-900/50 rounded-3xl p-6 sm:p-10 shadow-2xl space-y-8">
            <h3 className="text-xl font-bold font-serif text-amber-300 flex items-center gap-2 pb-4 border-b border-amber-900/40">
              <ShoppingBag className="w-5 h-5 text-amber-400" /> Thông Tin Đặt Hàng
            </h3>

            {orderSubmitted ? (
              <div className="py-12 text-center space-y-4 bg-amber-950/20 border border-amber-500/30 rounded-2xl p-6">
                <div className="w-16 h-16 bg-amber-500/20 rounded-full flex items-center justify-center mx-auto text-amber-400 border border-amber-500/40">
                  <Check className="w-8 h-8" />
                </div>
                <h4 className="text-2xl font-bold font-serif text-amber-200">
                  Đặt Hàng Thành Công!
                </h4>
                <p className="text-xs text-amber-100/70 max-w-md mx-auto leading-relaxed">
                  Cảm ơn Quý khách <strong>{formData.name}</strong> đã đặt mua Bộ Sưu Tập TỎA. Chuyên viên tư vấn của chúng tôi sẽ gọi lại xác nhận trong vòng 15 phút.
                </p>
                <button
                  onClick={() => setOrderSubmitted(false)}
                  className="px-6 py-2.5 rounded-full bg-amber-500 text-stone-950 font-semibold text-xs uppercase"
                >
                  Tạo Đơn Hàng Mới
                </button>
              </div>
            ) : (
              <form onSubmit={handleFormSubmit} className="space-y-6">
                
                {/* Package Choice */}
                <div className="space-y-3">
                  <label className="block text-xs font-semibold uppercase tracking-wider text-amber-200/80">
                    Chọn Loại Hộp Quà
                  </label>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                    <div 
                      onClick={() => setSelectedBoxType('full')}
                      className={`p-4 rounded-2xl border cursor-pointer transition-all ${
                        selectedBoxType === 'full' 
                          ? 'bg-amber-500/10 border-amber-400 ring-1 ring-amber-400' 
                          : 'bg-black/30 border-amber-900/40 hover:border-amber-700'
                      }`}
                    >
                      <div className="flex justify-between items-start mb-2">
                        <span className="font-bold font-serif text-amber-200">Hộp Hoàng Gia (Full)</span>
                        <span className="text-xs font-semibold text-amber-400">1.280.000đ</span>
                      </div>
                      <p className="text-[11px] text-amber-100/60">Gồm 4 bánh cao cấp + Đèn Lồng LED + Bộ Trà Ô Long Thượng Hạng.</p>
                    </div>

                    <div 
                      onClick={() => setSelectedBoxType('compact')}
                      className={`p-4 rounded-2xl border cursor-pointer transition-all ${
                        selectedBoxType === 'compact' 
                          ? 'bg-amber-500/10 border-amber-400 ring-1 ring-amber-400' 
                          : 'bg-black/30 border-amber-900/40 hover:border-amber-700'
                      }`}
                    >
                      <div className="flex justify-between items-start mb-2">
                        <span className="font-bold font-serif text-amber-200">Hộp Tiêu Chuẩn</span>
                        <span className="text-xs font-semibold text-amber-400">880.000đ</span>
                      </div>
                      <p className="text-[11px] text-amber-100/60">Gồm 4 bánh nghệ nhân + Đèn Lồng LED chiếu sáng.</p>
                    </div>
                  </div>
                </div>

                {/* Form Fields */}
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div className="space-y-1.5">
                    <label className="block text-xs font-medium text-amber-200/80">Họ và Tên *</label>
                    <input 
                      type="text" 
                      required
                      placeholder="Nguyễn Văn A" 
                      value={formData.name}
                      onChange={(e) => setFormData({...formData, name: e.target.value})}
                      className="w-full bg-black/40 border border-amber-900/50 rounded-xl px-4 py-3 text-sm text-amber-100 placeholder-amber-900/60 focus:outline-none focus:border-amber-400 transition-colors"
                    />
                  </div>

                  <div className="space-y-1.5">
                    <label className="block text-xs font-medium text-amber-200/80">Số Điện Thoại *</label>
                    <input 
                      type="tel" 
                      required
                      placeholder="0901 234 567" 
                      value={formData.phone}
                      onChange={(e) => setFormData({...formData, phone: e.target.value})}
                      className="w-full bg-black/40 border border-amber-900/50 rounded-xl px-4 py-3 text-sm text-amber-100 placeholder-amber-900/60 focus:outline-none focus:border-amber-400 transition-colors"
                    />
                  </div>
                </div>

                <div className="space-y-1.5">
                  <label className="block text-xs font-medium text-amber-200/80">Địa Chỉ Giao Hàng *</label>
                  <input 
                    type="text" 
                    required
                    placeholder="Số nhà, Tên đường, Phường/Xã, Quận/Huyện, TP..." 
                    value={formData.address}
                    onChange={(e) => setFormData({...formData, address: e.target.value})}
                    className="w-full bg-black/40 border border-amber-900/50 rounded-xl px-4 py-3 text-sm text-amber-100 placeholder-amber-900/60 focus:outline-none focus:border-amber-400 transition-colors"
                  />
                </div>

                {/* Quantity Control */}
                <div className="flex items-center justify-between p-4 bg-black/40 border border-amber-900/50 rounded-2xl">
                  <div>
                    <span className="text-sm font-semibold text-amber-200 block">Số Lượng Hộp</span>
                    <span className="text-[11px] text-amber-400/70">Giảm 10% cho đơn hàng từ 5 hộp</span>
                  </div>
                  <div className="flex items-center gap-3">
                    <button
                      type="button"
                      onClick={() => setOrderQuantity(Math.max(1, orderQuantity - 1))}
                      className="w-9 h-9 rounded-lg bg-amber-950/60 border border-amber-800/40 text-amber-200 font-bold hover:bg-amber-900 transition-colors"
                    >
                      -
                    </button>
                    <span className="w-8 text-center font-bold text-lg text-amber-300 font-serif">
                      {orderQuantity}
                    </span>
                    <button
                      type="button"
                      onClick={() => setOrderQuantity(orderQuantity + 1)}
                      className="w-9 h-9 rounded-lg bg-amber-950/60 border border-amber-800/40 text-amber-200 font-bold hover:bg-amber-900 transition-colors"
                    >
                      +
                    </button>
                  </div>
                </div>

                {/* Submit Button */}
                <button
                  type="submit"
                  disabled={isSubmitting}
                  className="w-full py-4 rounded-full bg-gradient-to-r from-amber-300 via-amber-400 to-amber-500 hover:brightness-110 text-stone-950 font-bold text-sm uppercase tracking-widest shadow-[0_0_25px_rgba(245,158,11,0.3)] transition-all duration-300 flex items-center justify-center gap-2"
                >
                  {isSubmitting ? (
                    <span className="inline-block animate-spin font-sans">⌛ Đang gửi thông tin...</span>
                  ) : (
                    <>Xác Nhận Đặt Hàng ({finalPrice.toLocaleString('vi-VN')}đ)</>
                  )}
                </button>

              </form>
            )}
          </div>

          {/* Right Summary Column */}
          <div className="lg:col-span-5 space-y-6">
            
            <div className="bg-[#180A0E] border border-amber-900/40 rounded-3xl p-6 sm:p-8 space-y-6">
              <h4 className="text-lg font-bold font-serif text-amber-300 pb-3 border-b border-amber-900/40">
                Tóm Tắt Đơn Hàng
              </h4>

              <div className="space-y-4 text-xs">
                <div className="flex justify-between text-amber-100/80">
                  <span>Loại hộp đã chọn:</span>
                  <span className="font-semibold text-amber-300">
                    {selectedBoxType === 'full' ? "Hộp Hoàng Gia" : "Hộp Tiêu Chuẩn"}
                  </span>
                </div>

                <div className="flex justify-between text-amber-100/80">
                  <span>Số lượng:</span>
                  <span className="font-semibold text-amber-300">{orderQuantity} Hộp</span>
                </div>

                <div className="flex justify-between text-amber-100/80">
                  <span>Đơn giá:</span>
                  <span>{unitPrice.toLocaleString('vi-VN')}đ / hộp</span>
                </div>

                {discount > 0 && (
                  <div className="flex justify-between text-emerald-400 font-medium">
                    <span>Ưu đãi mua nhiều (10%):</span>
                    <span>-{discount.toLocaleString('vi-VN')}đ</span>
                  </div>
                )}

                <div className="pt-4 border-t border-amber-900/40 flex justify-between items-baseline">
                  <span className="text-sm font-semibold text-white">Tổng Thanh Toán:</span>
                  <span className="text-2xl font-bold font-serif text-amber-400">
                    {finalPrice.toLocaleString('vi-VN')}đ
                  </span>
                </div>
              </div>
            </div>

            {/* Service Guarantees */}
            <div className="grid grid-cols-2 gap-4">
              <div className="p-4 rounded-2xl bg-[#160A0D] border border-amber-900/30 flex items-start gap-3">
                <ShieldCheck className="w-5 h-5 text-amber-400 flex-shrink-0 mt-0.5" />
                <div>
                  <h5 className="text-xs font-bold text-amber-200 mb-1">Cam Kết Chất Lượng</h5>
                  <p className="text-[11px] text-amber-100/60 leading-tight">100% nguyên liệu tươi mới, vệ sinh an toàn thực phẩm chuẩn ISO.</p>
                </div>
              </div>

              <div className="p-4 rounded-2xl bg-[#160A0D] border border-amber-900/30 flex items-start gap-3">
                <Truck className="w-5 h-5 text-amber-400 flex-shrink-0 mt-0.5" />
                <div>
                  <h5 className="text-xs font-bold text-amber-200 mb-1">Giao Hàng Tận Nơi</h5>
                  <p className="text-[11px] text-amber-100/60 leading-tight">Đóng gói chống va đập chuyên dụng, giao nhanh trong 24h.</p>
                </div>
              </div>
            </div>

          </div>

        </div>
      </section>

      {/* ================= FOOTER ================= */}
      <footer className="border-t border-amber-900/40 bg-[#0A0406] py-12 text-xs text-amber-200/60">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 grid grid-cols-1 md:grid-cols-4 gap-8">
          
          <div className="space-y-3">
            <div className="flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-amber-400" />
              <span className="text-base font-bold font-serif text-amber-300">TỎA MOONCAKE</span>
            </div>
            <p className="text-amber-100/50 text-[11px] leading-relaxed">
              Thương hiệu quà tặng Trung Thu cao cấp. Mang trọn nghệ thuật lồng đèn dân tộc vào kiệt tác bánh nướng truyền thống.
            </p>
          </div>

          <div className="space-y-2">
            <h5 className="font-bold text-amber-300 text-xs uppercase tracking-wider">Liên Hệ</h5>
            <p className="flex items-center gap-2"><Phone className="w-3.5 h-3.5 text-amber-400" /> 1900 888 999</p>
            <p className="flex items-center gap-2"><Mail className="w-3.5 h-3.5 text-amber-400" /> contact@toamooncake.vn</p>
          </div>

          <div className="space-y-2">
            <h5 className="font-bold text-amber-300 text-xs uppercase tracking-wider">Địa Chỉ Showroom</h5>
            <p className="flex items-start gap-2"><MapPin className="w-3.5 h-3.5 text-amber-400 flex-shrink-0 mt-0.5" /> 128 Nguyễn Huệ, Quận 1, Thành phố Hồ Chí Minh</p>
          </div>

          <div className="space-y-2">
            <h5 className="font-bold text-amber-300 text-xs uppercase tracking-wider">Chính Sách</h5>
            <p>• Chính sách bảo mật thông tin</p>
            <p>• Chính sách đổi trả & hoàn tiền</p>
            <p>• Vận chuyển & Giao nhận</p>
          </div>

        </div>

        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 mt-12 pt-6 border-t border-amber-900/20 text-center text-[11px] text-amber-200/40">
          © 2024 TỎA Mooncake Collection. Designed with ❤️ in Vietnam. All rights reserved.
        </div>
      </footer>

    </div>
  );
}
