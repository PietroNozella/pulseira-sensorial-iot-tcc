import 'package:flutter/material.dart';

import '../../../../core/theme/app_colors.dart';
import '../../../../services/storage_service.dart';

class ProfileScreen extends StatelessWidget {
	const ProfileScreen({
		super.key,
	});

	Future<void> _fazerLogout(BuildContext context) async {
		await StorageService().deleteToken();

		if (!context.mounted) return;

		Navigator.pushNamedAndRemoveUntil(
			context,
			'/',
			(route) => false,
		);
	}

	@override
	Widget build(BuildContext context) {
		return SafeArea(
			child: Center(
				child: Padding(
					padding: const EdgeInsets.symmetric(horizontal: 20),
					child: SizedBox(
						width: double.infinity,
						child: OutlinedButton.icon(
							onPressed: () => _fazerLogout(context),
							icon: const Icon(Icons.logout_rounded, color: AppColors.error),
							label: const Text(
								'Sair',
								style: TextStyle(color: AppColors.error),
							),
							style: OutlinedButton.styleFrom(
								backgroundColor: AppColors.transparent,
								side: const BorderSide(color: AppColors.error, width: 1.5),
								shape: RoundedRectangleBorder(
									borderRadius: BorderRadius.circular(24),
								),
								padding: const EdgeInsets.symmetric(horizontal: 28, vertical: 14),
							),
						),
					),
				),
			),
		);
	}
}
