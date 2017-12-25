import qbs 1.0

Project {
	references: [ buildDirectory + '/../conanbuildinfo.qbs' ]
	Product {
		type: 'application'
		consoleApplication: true

		Depends { name: 'ConanBasicSetup' }

		Depends { name: 'cpp' }
		cpp.compilerPathByLanguage: ({
			c: '/usr/local/bin/clang',
			cpp: '/usr/local/bin/clang++',
		})
		cpp.cxxStandardLibrary: 'libstdc++'
		cpp.linkerPath: '/usr/local/bin/clang++'
		cpp.linkerWrapper: undefined
		cpp.minimumMacosVersion: '10.10'
		cpp.rpaths: [ buildDirectory + '/../../bin' ]
		cpp.target: 'x86_64-apple-macosx10.10'

		Depends { name: 'xcode' }
		xcode.sdk: 'macosx10.10'

		files: [ 'test_package.cc' ]
	}
}
