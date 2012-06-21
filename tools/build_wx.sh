#!/bin/bash
WXVER=2.8.12.1
set -o errexit
if [ ! -e wxPython-src-${WXVER}.tar.bz2 ]; then
    wget http://downloads.sourceforge.net/project/wxpython/wxPython/${WXVER}/wxPython-src-${WXVER}.tar.bz2
fi
rm -rf wxPython-src-${WXVER}
tar xvjf wxPython-src-${WXVER}.tar.bz2
cd wxPython-src-${WXVER}
export WXWIN="$PWD"
cd build
"$WXWIN/configure" \
    --disable-rpath \
    --enable-debug=0 \
    --enable-optimise \
    --enable-monolithic \
    --enable-unicode \
    --with-gtk \
    --with-expat=builtin \
    --with-libpng=builtin \
    --with-libjpeg=builtin \
    --with-libtiff=builtin \
    --with-zlib=no \
    --with-regex=no
make
make -C contrib/src/stc
make -C contrib/src/gizmos
cd "$WXWIN/wxPython"
export LDFLAGS=-Wl,-rpath=\\\$ORIGIN
python2.7 setup.py build_ext --inplace \
    UNICODE=1 \
    MONOLITHIC=1 \
    WX_CONFIG="$WXWIN/build/wx-config" \
    BUILD_GLCANVAS=0
cd "$WXWIN"
mv wxPython/wx ../
cp build/lib/libwx_gtk2u*-2.8.so.0 ../wx/
cd ..
strip -s -R .comment wx/*.so*
rm -rf wxPython-src-${WXVER}
