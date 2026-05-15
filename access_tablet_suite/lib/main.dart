import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  // Lock orientations to Tablet-friendly landscape/portrait mixes if needed
  SystemChrome.setPreferredOrientations([
    DeviceOrientation.portraitUp,
    DeviceOrientation.landscapeLeft,
    DeviceOrientation.landscapeRight,
  ]);
  runApp(const AccessTabletApp());
}

class AccessTabletApp extends StatelessWidget {
  const AccessTabletApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Access Paralegal Suite',
      debugShowCheckedModeBanner: false,
      
      // --- AUTOMATIC THEME ENGINE (Ties directly to iOS/Android settings) ---
      themeMode: ThemeMode.system, 
      
      // ☀️ LIGHT MODE THEME (Silver/Clean)
      theme: ThemeData(
        useMaterial3: true,
        colorScheme: ColorScheme.fromSeed(
          seedColor: const Color(0xFF288F4F),
          brightness: Brightness.light,
          background: const Color(0xFFF3F4F6), // Light Silver
          surface: Colors.white,
        ),
        appBarTheme: const AppBarTheme(
          backgroundColor: Colors.white,
          foregroundColor: Color(0xFF1F2937),
          elevation: 0,
        ),
      ),

      // 🌙 DARK MODE THEME (Deep Organic Gray)
      darkTheme: ThemeData(
        useMaterial3: true,
        colorScheme: ColorScheme.fromSeed(
          seedColor: const Color(0xFF288F4F),
          brightness: Brightness.dark,
          background: const Color(0xFF121413),
          surface: const Color(0xFF1E211F),
        ),
        appBarTheme: const AppBarTheme(
          backgroundColor: Color(0xFF1E211F),
          elevation: 0,
        ),
      ),

      home: const TabletDashboard(),
    );
  }
}

class TabletDashboard extends StatefulWidget {
  const TabletDashboard({super.key});

  @override
  State<TabletDashboard> createState() => _TabletDashboardState();
}

class _TabletDashboardState extends State<TabletDashboard> {
  @override
  Widget build(BuildContext context) {
    final isLargeScreen = MediaQuery.of(context).size.width > 600;

    return Scaffold(
      body: Row(
        children: [
          // --- ADAPTIVE TABLET NAVIGATION RAIL (iOS/Android Native Style) ---
          if (isLargeScreen)
            NavigationRail(
              selectedIndex: 0,
              labelType: NavigationRailLabelType.all,
              leading: Padding(
                padding: const EdgeInsets.symmetric(vertical: 24),
                child: Container(
                  width: 50,
                  height: 50,
                  decoration: const BoxDecoration(
                    color: Color(0xFF288F4F),
                    shape: BoxShape.circle,
                  ),
                  child: const Center(
                    child: Text("AP", style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
                  ),
                ),
              ),
              destinations: const [
                NavigationRailDestination(icon: Icon(Icons.folder_copy_rounded), label: Text('PDF Merger')),
                NavigationRailDestination(icon: Icon(Icons.mail_outline), label: Text('Email Rip')),
                NavigationRailDestination(icon: Icon(Icons.settings_suggest_outlined), label: Text('Settings')),
              ],
            ),
          
          const VerticalDivider(thickness: 1, width: 1),
          
          // --- MAIN APP CONTENT AREA ---
          Expanded(
            child: CustomScrollView(
              slivers: [
                const SliverAppBar.large(
                  title: Text(
                    "Access Paralegal",
                    style: TextStyle(fontWeight: FontWeight.bold),
                  ),
                  actions: [
                     Padding(
                       padding: EdgeInsets.only(right: 16.0),
                       child: Chip(
                         label: Text("Tablet Client"),
                         backgroundColor: Color(0x1A288F4F),
                       ),
                     )
                  ],
                ),
                SliverToBoxAdapter(
                  child: Padding(
                    padding: const EdgeInsets.all(24.0),
                    child: GridView.count(
                      shrinkWrap: true,
                      physics: const NeverScrollableScrollPhysics(),
                      crossAxisCount: isLargeScreen ? 2 : 1,
                      mainAxisSpacing: 20,
                      crossAxisSpacing: 20,
                      childAspectRatio: 1.6,
                      children: [
                        _buildFeatureCard(
                          context,
                          title: "Reconstructive PDF Merger",
                          subtitle: "Select local directories or iOS Files bundles to execute 1:1 Audited mergers.",
                          icon: Icons.merge_type,
                        ),
                        _buildFeatureCard(
                          context,
                          title: "Offline Email Attachment Harvester",
                          subtitle: "Ingest .eml / .msg streams and extract PDF attachments directly in hardware memory.",
                          icon: Icons.mark_email_unread_rounded,
                        ),
                      ],
                    ),
                  ),
                )
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildFeatureCard(BuildContext context, {required String title, required String subtitle, required IconData icon}) {
    final colorScheme = Theme.of(context).colorScheme;
    return Card(
      elevation: 0,
      color: colorScheme.surface,
      shape: RoundedRectangleBorder(
        side: BorderSide(color: colorScheme.outlineVariant.withOpacity(0.5)),
        borderRadius: BorderRadius.circular(16),
      ),
      child: InkWell(
        borderRadius: BorderRadius.circular(16),
        onTap: () {},
        child: Padding(
          padding: const EdgeInsets.all(24.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Icon(icon, size: 36, color: const Color(0xFF288F4F)),
              Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(title, style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
                  const SizedBox(height: 8),
                  Text(subtitle, style: TextStyle(color: colorScheme.onSurfaceVariant, fontSize: 13)),
                ],
              )
            ],
          ),
        ),
      ),
    );
  }
}
