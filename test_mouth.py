#!/usr/bin/env python3
"""
Comprehensive test suite for Mouth TTS on Raspberry Pi
Tests performance, memory usage, audio compatibility, and Pi-specific features
"""

import time
import psutil
import sounddevice as sd
import subprocess
import platform
import sys
from mouth import Mouth

class PiTester:
    """Test suite optimized for Raspberry Pi environment"""
    
    def __init__(self):
        self.mouth = None
        self.test_results = []
        self.start_memory = psutil.virtual_memory().percent
        
    def log_test(self, test_name, success, details="", duration=0, memory_used=0):
        """Log test results"""
        result = {
            'test': test_name,
            'success': success,
            'details': details,
            'duration': duration,
            'memory_used': memory_used
        }
        self.test_results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {details}")
        if duration > 0:
            print(f"   ⏱️  Duration: {duration:.2f}s")
        if memory_used > 0:
            print(f"   🧠 Memory: +{memory_used:.1f}%")

    def get_system_info(self):
        """Get Raspberry Pi system information"""
        print("=== SYSTEM INFORMATION ===")
        try:
            # CPU info
            with open('/proc/cpuinfo', 'r') as f:
                cpuinfo = f.read()
                if 'Raspberry Pi' in cpuinfo:
                    print("🍓 Raspberry Pi detected")
                    # Extract Pi model
                    for line in cpuinfo.split('\n'):
                        if 'Model' in line:
                            print(f"   {line.strip()}")
                            break
                else:
                    print(f"📱 Platform: {platform.machine()}")
            
            # Memory info
            memory = psutil.virtual_memory()
            print(f"💾 RAM: {memory.total // (1024**3):.1f}GB total, {memory.available // (1024**3):.1f}GB available ({memory.percent:.1f}% used)")
            
            # CPU info
            print(f"🔧 CPU: {psutil.cpu_count()} cores, {psutil.cpu_freq().current:.0f}MHz")
            
            # Audio devices
            print("🔊 Audio devices:")
            try:
                devices = sd.query_devices()
                for i, device in enumerate(devices):
                    if device['max_output_channels'] > 0:
                        print(f"   [{i}] {device['name']} ({device['max_output_channels']} ch, {device['default_samplerate']:.0f}Hz)")
            except Exception as e:
                print(f"   Audio device query failed: {e}")
                
        except Exception as e:
            print(f"⚠️  System info error: {e}")
        print()

    def test_initialization(self):
        """Test Mouth class initialization"""
        print("=== INITIALIZATION TESTS ===")
        
        start_time = time.time()
        start_mem = psutil.virtual_memory().percent
        
        try:
            self.mouth = Mouth(chunk_size=512)  # Smaller chunk for Pi
            duration = time.time() - start_time
            memory_used = psutil.virtual_memory().percent - start_mem
            
            self.log_test("Mouth initialization", True, 
                         f"Initialized successfully", duration, memory_used)
            
            # Test Pi detection
            if hasattr(self.mouth, 'is_raspberry_pi'):
                pi_detected = self.mouth.is_raspberry_pi
                self.log_test("Pi detection", True, 
                             f"Pi detected: {pi_detected}")
            
        except Exception as e:
            duration = time.time() - start_time
            self.log_test("Mouth initialization", False, f"Failed: {e}", duration)
            return False
            
        print()
        return True

    def test_basic_speech(self):
        """Test basic text-to-speech functionality"""
        print("=== BASIC SPEECH TESTS ===")
        
        test_phrases = [
            "Hello, this is a test.",
            "Testing Raspberry Pi text to speech.",
            "Short test.",
            "This is a longer sentence to test audio processing on Raspberry Pi systems with potentially limited resources."
        ]
        
        for i, phrase in enumerate(test_phrases, 1):
            start_time = time.time()
            start_mem = psutil.virtual_memory().percent
            
            try:
                self.mouth.speak(phrase)
                duration = time.time() - start_time
                memory_used = psutil.virtual_memory().percent - start_mem
                
                self.log_test(f"Speech test {i}", True, 
                             f"'{phrase[:30]}...' ({len(phrase)} chars)", 
                             duration, memory_used)
                             
                # Brief pause between tests
                time.sleep(0.5)
                
            except Exception as e:
                duration = time.time() - start_time
                self.log_test(f"Speech test {i}", False, f"Failed: {e}", duration)
        
        print()

    def test_memory_stress(self):
        """Test memory usage under stress"""
        print("=== MEMORY STRESS TESTS ===")
        
        # Test with various text lengths
        stress_tests = [
            ("Short text", "Hello world!" * 5),
            ("Medium text", "This is a medium length text for testing. " * 10),
            ("Long text", "This is a very long text that should test memory usage on Raspberry Pi systems. " * 25)
        ]
        
        initial_memory = psutil.virtual_memory().percent
        
        for test_name, text in stress_tests:
            start_time = time.time()
            start_mem = psutil.virtual_memory().percent
            
            try:
                self.mouth.speak(text)
                duration = time.time() - start_time
                memory_used = psutil.virtual_memory().percent - start_mem
                final_memory = psutil.virtual_memory().percent
                
                # Check for memory leaks
                leak_detected = final_memory > initial_memory + 5  # 5% tolerance
                
                self.log_test(f"Memory stress: {test_name}", not leak_detected,
                             f"Length: {len(text)} chars, Leak: {leak_detected}",
                             duration, memory_used)
                             
                time.sleep(1)  # Allow GC
                
            except Exception as e:
                duration = time.time() - start_time
                self.log_test(f"Memory stress: {test_name}", False, f"Failed: {e}", duration)
        
        print()

    def test_audio_compatibility(self):
        """Test audio system compatibility"""
        print("=== AUDIO COMPATIBILITY TESTS ===")
        
        try:
            # Test different sample rates
            test_rates = [16000, 22050, 44100, 48000]
            for rate in test_rates:
                try:
                    # Quick audio test without TTS
                    import numpy as np
                    duration = 0.1  # 100ms
                    t = np.linspace(0, duration, int(duration * rate))
                    tone = np.sin(2 * np.pi * 440 * t) * 0.1  # Quiet 440Hz tone
                    
                    sd.play(tone, rate)
                    sd.wait()
                    
                    self.log_test(f"Audio test {rate}Hz", True, "Audio device compatible")
                    
                except Exception as e:
                    self.log_test(f"Audio test {rate}Hz", False, f"Failed: {e}")
                    
        except Exception as e:
            self.log_test("Audio compatibility", False, f"Audio system error: {e}")
        
        print()

    def test_performance_benchmark(self):
        """Benchmark performance metrics"""
        print("=== PERFORMANCE BENCHMARK ===")
        
        benchmark_text = "This is a performance benchmark test for Raspberry Pi text to speech."
        iterations = 3
        
        times = []
        memory_peaks = []
        
        for i in range(iterations):
            start_time = time.time()
            start_mem = psutil.virtual_memory().percent
            peak_mem = start_mem
            
            try:
                self.mouth.speak(benchmark_text)
                
                # Monitor peak memory during execution
                current_mem = psutil.virtual_memory().percent
                if current_mem > peak_mem:
                    peak_mem = current_mem
                
                duration = time.time() - start_time
                times.append(duration)
                memory_peaks.append(peak_mem - start_mem)
                
            except Exception as e:
                self.log_test(f"Benchmark iteration {i+1}", False, f"Failed: {e}")
                return
        
        if times:
            avg_time = sum(times) / len(times)
            avg_memory = sum(memory_peaks) / len(memory_peaks)
            
            # Performance thresholds for Pi
            time_ok = avg_time < 10.0  # Should complete within 10 seconds
            memory_ok = avg_memory < 20.0  # Should use less than 20% additional memory
            
            self.log_test("Performance benchmark", time_ok and memory_ok,
                         f"Avg: {avg_time:.2f}s, Mem: +{avg_memory:.1f}%")
        
        print()

    def test_edge_cases(self):
        """Test edge cases and error handling"""
        print("=== EDGE CASE TESTS ===")
        
        edge_cases = [
            ("Empty string", ""),
            ("Only spaces", "   "),
            ("Numbers", "12345 67890"),
            ("Special chars", "Hello! How are you? I'm fine, thanks."),
            ("Unicode", "Café, naïve, résumé"),
        ]
        
        for test_name, text in edge_cases:
            start_time = time.time()
            
            try:
                self.mouth.speak(text)
                duration = time.time() - start_time
                
                # Empty/space strings should return quickly
                if text.strip() == "":
                    success = duration < 0.1
                    details = f"Quick return: {duration:.3f}s"
                else:
                    success = True
                    details = "Handled correctly"
                
                self.log_test(f"Edge case: {test_name}", success, details, duration)
                
            except Exception as e:
                duration = time.time() - start_time
                self.log_test(f"Edge case: {test_name}", False, f"Failed: {e}", duration)
        
        print()

    def test_resource_cleanup(self):
        """Test resource cleanup and garbage collection"""
        print("=== RESOURCE CLEANUP TESTS ===")
        
        initial_memory = psutil.virtual_memory().percent
        
        # Generate some temporary files and memory usage
        for i in range(5):
            try:
                self.mouth.speak(f"Cleanup test number {i+1}")
            except:
                pass
        
        # Force garbage collection
        import gc
        gc.collect()
        time.sleep(1)
        
        final_memory = psutil.virtual_memory().percent
        memory_diff = final_memory - initial_memory
        
        # Check if memory was properly cleaned up
        cleanup_ok = memory_diff < 5.0  # Less than 5% memory increase
        
        self.log_test("Resource cleanup", cleanup_ok,
                     f"Memory change: {memory_diff:+.1f}%")
        
        print()

    def run_all_tests(self):
        """Run all tests and provide summary"""
        print("🍓 RASPBERRY PI TTS TEST SUITE 🍓")
        print("=" * 50)
        
        self.get_system_info()
        
        # Run test suite
        if not self.test_initialization():
            print("❌ Initialization failed - stopping tests")
            return
        
        self.test_basic_speech()
        self.test_memory_stress()
        self.test_audio_compatibility()
        self.test_performance_benchmark()
        self.test_edge_cases()
        self.test_resource_cleanup()
        
        # Summary
        print("=== TEST SUMMARY ===")
        passed = sum(1 for r in self.test_results if r['success'])
        total = len(self.test_results)
        
        print(f"Tests passed: {passed}/{total}")
        print(f"Success rate: {passed/total*100:.1f}%")
        
        # Show failed tests
        failed_tests = [r for r in self.test_results if not r['success']]
        if failed_tests:
            print("\n❌ Failed tests:")
            for test in failed_tests:
                print(f"   • {test['test']}: {test['details']}")
        
        # Performance summary
        durations = [r['duration'] for r in self.test_results if r['duration'] > 0]
        if durations:
            avg_duration = sum(durations) / len(durations)
            print(f"\n⏱️  Average test duration: {avg_duration:.2f}s")
        
        memory_usage = psutil.virtual_memory().percent - self.start_memory
        print(f"🧠 Total memory change: {memory_usage:+.1f}%")
        
        return passed == total

def main():
    """Main test function"""
    try:
        tester = PiTester()
        success = tester.run_all_tests()
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\n⚠️  Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Test suite crashed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 
